#!/usr/bin/env python3
"""Capture public RPC observations without proxy discovery or redirects."""
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sibling(folder, filename):
    spec = importlib.util.spec_from_file_location('direct_' + folder.replace('-', '_'),
                                                ROOT / folder / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rpc = sibling('rpc-snapshot', 'rpc_snapshot.py')
pinned = sibling('pinned-snapshot', 'pinned_snapshot.py')
check = sibling('snapshot-check', 'check_snapshot.py')
MAX_INPUT = 65536
MAX_BYTES = rpc.MAX_RESPONSE_BYTES
USER_AGENT = 'Pepeolithic-Direct-Capture/1.0 (read-only Ethereum observations)'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('non-finite JSON value')


def parse(raw, limit=None):
    limit = MAX_BYTES if limit is None else limit
    if len(raw) > limit:
        raise ValueError('JSON size limit exceeded')
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('RPC redirects are refused')


def public_read(endpoint, method, params):
    # Validate before constructing an opener, resolving DNS, or sending anything.
    rpc.validate_endpoint(endpoint)
    rpc.validate_request(method, params)
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params},
                      allow_nan=False).encode('utf-8')
    if len(body) > MAX_INPUT:
        raise ValueError('RPC request exceeds 64 KiB')
    request = urllib.request.Request(endpoint, data=body, headers={
        'Content-Type': 'application/json', 'Accept': 'application/json',
        'Accept-Encoding': 'identity', 'User-Agent': USER_AGENT})
    # An explicit empty ProxyHandler prevents urllib from consulting environment
    # proxy settings. NoRedirect forbids moving a request to another endpoint.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError('RPC requires HTTP 200')
        if response.headers.get('Content-Encoding', 'identity').lower() != 'identity':
            raise ValueError('compressed RPC responses are unsupported')
        raw = response.read(MAX_BYTES + 1)
    payload = parse(raw)
    if (not isinstance(payload, dict) or set(payload) != {'jsonrpc', 'id', 'result'}):
        # Never echo a provider error, its URL, or its response body.
        raise ValueError('expected successful JSON-RPC response envelope')
    return rpc.validate_response(payload)


def capture(endpoint, method='eth_blockNumber', params=None):
    params = [] if params is None else params
    result = public_read(endpoint, method, params)
    snapshot = {'captured_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'endpoint': endpoint, 'method': method, 'params': params, 'result': result}
    check.summarize(snapshot)
    encode(snapshot)
    return snapshot


def capture_pinned(endpoint, tag='finalized'):
    # Reuse the ancestor's chain, exact-number, uint256 and before/after checks.
    return pinned.capture(endpoint, tag, read=lambda method, params:
                          public_read(endpoint, method, params))


def encode(value):
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('serialized snapshot exceeds 4 MiB')
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    one = commands.add_parser('capture', help='one allowlisted read; snapshot on stdout')
    one.add_argument('--rpc', required=True)
    one.add_argument('method', nargs='?', default='eth_blockNumber')
    one.add_argument('params', nargs='?', default='[]')
    pin = commands.add_parser('pinned', help='mainnet ZTO supply with number-pinned anchor checks')
    pin.add_argument('--rpc', required=True)
    pin.add_argument('--block', default='finalized')
    commands.add_parser('demo', help='offline inspection of retained real ZTO evidence')
    args = parser.parse_args()
    try:
        if args.command == 'capture':
            params = parse(args.params.encode('utf-8'), MAX_INPUT)
            output = capture(args.rpc, args.method, params)
        elif args.command == 'pinned':
            output = capture_pinned(args.rpc, args.block)
        else:
            raw = Path(__file__).with_name('example-pinned-zto.json').read_bytes()
            output = pinned.inspect(parse(raw))
            output['network_used'] = False
        sys.stdout.write(encode(output))
        return 0
    except (ValueError, TypeError, KeyError, RuntimeError, OSError, RecursionError):
        print('direct-capture: invalid input, inconsistent evidence, or RPC failure; no snapshot emitted',
              file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
