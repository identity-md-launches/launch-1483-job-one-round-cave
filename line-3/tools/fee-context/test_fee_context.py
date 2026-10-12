#!/usr/bin/env python3
"""Offline arithmetic, original-input and CLI regressions; no public requests."""
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import fee_context as f


class FeeTests(unittest.TestCase):
    def tx(self, cap=100, tip=10, gas=21000, value=7, chain=1):
        obj = f.reader.demo_object()
        obj.update(maxFeePerGas=hex(cap), maxPriorityFeePerGas=hex(tip),
                   gas=hex(gas), value=hex(value), chainId=hex(chain))
        return json.dumps(obj)

    def inspect(self, base, **kw):
        return f.inspect(self.tx(**kw), base, kw.get('chain', 1), 'json')

    def test_full_priority(self):
        r = self.inspect(80)
        self.assertTrue(r['passesCheckedFeeConstraints'])
        x = r['fees']
        self.assertEqual(x['effectiveGasPriceWei'], '90')
        self.assertEqual(x['effectivePriorityFeePerGasWei'], '10')
        self.assertEqual(x['contextFeeCeilingAtGasLimitWei'], '1890000')
        self.assertEqual(x['valuePlusFeeCeilingWei'], '2100007')
        self.assertEqual(x['maxBaseFeeForFullPriorityWei'], '90')
        self.assertTrue(x['fullPriorityAvailable'])

    def test_priority_clipped(self):
        x = self.inspect(95)['fees']
        self.assertEqual(x['effectiveGasPriceWei'], '100')
        self.assertEqual(x['effectivePriorityFeePerGasWei'], '5')
        self.assertFalse(x['fullPriorityAvailable'])

    def test_cap_boundary(self):
        r = self.inspect(100)
        self.assertTrue(r['passesCheckedFeeConstraints'])
        self.assertEqual(r['fees']['effectivePriorityFeePerGasWei'], '0')
        self.assertEqual(r['fees']['effectiveGasPriceWei'], '100')

    def test_base_fee_above_cap(self):
        r = self.inspect(101)
        self.assertEqual(r['checkedViolations'], ['base-fee-exceeds-max-fee'])
        self.assertEqual(r['fees']['baseFeeShortfallPerGasWei'], '1')
        self.assertIsNone(r['fees']['effectiveGasPriceWei'])
        self.assertIsNone(r['fees']['contextBurnCeilingAtGasLimitWei'])

    def test_invalid_fee_order_even_at_zero_base(self):
        r = self.inspect(0, cap=9, tip=10)
        self.assertEqual(r['checkedViolations'], ['priority-fee-exceeds-max-fee'])
        self.assertIsNone(r['fees']['maxBaseFeeForFullPriorityWei'])
        self.assertIsNone(r['fees']['effectivePriorityFeePerGasWei'])

    def test_two_violations(self):
        r = self.inspect(11, cap=9, tip=10)
        self.assertEqual(len(r['checkedViolations']), 2)

    def test_zero_fees_and_gas(self):
        r = self.inspect(0, cap=0, tip=0, gas=0, value=0)
        self.assertTrue(r['passesCheckedFeeConstraints'])
        self.assertEqual(r['fees']['contextFeeCeilingAtGasLimitWei'], '0')
        # Intentionally fee checks only, not an intrinsic-gas verdict.
        self.assertTrue(r['fees']['fullPriorityAvailable'])

    def test_maximum_uint256_exact_products(self):
        r = self.inspect(f.UINT256_MAX, cap=f.UINT256_MAX, tip=0,
                         gas=f.UINT256_MAX, value=f.UINT256_MAX)
        self.assertEqual(int(r['fees']['valuePlusFeeCeilingWei']),
                         f.UINT256_MAX**2 + f.UINT256_MAX)

    def test_chain_context(self):
        with self.assertRaisesRegex(ValueError, 'does not match'):
            f.inspect(self.tx(), 1, 2, 'json')
        r = self.inspect(1, chain=2)
        self.assertEqual(r['fees']['nativeFeeAsset'], 'Unspecified chain native asset')

    def test_context_type_and_range(self):
        for bad in (True, -1, 1.0, '1', f.UINT256_MAX+1):
            with self.assertRaises(ValueError):
                f.inspect(self.tx(), bad, 1, 'json')
        for bad in (True, 0, -1, 1.0, f.UINT256_MAX+1):
            with self.assertRaises(ValueError):
                f.inspect(self.tx(), 1, bad, 'json')

    def test_canonical_decimal(self):
        for text in ('00', '+1', '-1', '1.0', '0x1', ' 1', '1\n', '1e9', '', '9'*79,
                     str(f.UINT256_MAX+1)):
            with self.assertRaises(ValueError):
                f.decimal(text)
        self.assertEqual(f.decimal('0'), 0)
        self.assertEqual(f.decimal(str(f.UINT256_MAX)), f.UINT256_MAX)

    def test_original_input_equivalence(self):
        a = f.inspect(f.reader.D.demo_transaction(), 1000000000, 1)
        b = f.inspect(json.dumps(f.reader.demo_object()), 1000000000, 1, 'json')
        self.assertEqual(a['fees'], b['fees'])
        self.assertEqual(a['inspection'], b['inspection'])

    def test_reject_signed_ambiguous_summary_and_oversize(self):
        obj = f.reader.demo_object()
        for key in ('from', 'r', 's', 'yParity'):
            bad = dict(obj, **{key: '0x0'})
            with self.assertRaises(ValueError):
                f.inspect(json.dumps(bad), 1, 1, 'json')
        for text in ('{"type":"0x2","type":"0x2"}', '{"inspection":{}}',
                     '['*2000, 'x'*(f.MAX_INPUT_CHARS+1)):
            with self.assertRaises(ValueError):
                f.inspect(text, 1, 1, 'json')
        with self.assertRaises(ValueError):
            f.inspect('0x02c0', 1, 1)
        with self.assertRaises(ValueError):
            f.inspect(self.tx(), 1, 1, 'summary')

    def test_independent_random_arithmetic(self):
        rng = random.Random(28)
        for _ in range(150):
            cap, tip, base = (rng.randrange(0, 10**18) for _ in range(3))
            gas = rng.randrange(0, 10**8)
            r = self.inspect(base, cap=cap, tip=tip, gas=gas)
            valid = cap >= base and cap >= tip
            self.assertEqual(r['passesCheckedFeeConstraints'], valid)
            if valid:
                # Algebraically equivalent independent expression.
                price = min(cap, base+tip)
                self.assertEqual(int(r['fees']['effectiveGasPriceWei']), price)
                self.assertEqual(int(r['fees']['contextFeeCeilingAtGasLimitWei']), gas*price)
                self.assertEqual(int(r['fees']['contextBurnCeilingAtGasLimitWei']) +
                                 int(r['fees']['contextPriorityCeilingAtGasLimitWei']), gas*price)

    def test_cli_exit_and_stdin(self):
        script = str(Path(f.__file__).resolve())
        prefix = [sys.executable, '-B', script, '--context-chain', '1', '--base-fee-wei']
        ok = subprocess.run(prefix+['1000000000', '--demo'], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)['schema'], 'fee-context/v1')
        fail = subprocess.run(prefix+['3000000000', '--demo'], capture_output=True, text=True)
        self.assertEqual(fail.returncode, 1, fail.stderr)
        self.assertFalse(json.loads(fail.stdout)['passesCheckedFeeConstraints'])
        for args, text in ((['01', '--demo'], ''),
                           (['1', '--format', 'json', '--stdin'], '{"r":"0x1"}'),
                           (['1', '--stdin'], 'x'*(f.MAX_INPUT_CHARS+1))):
            bad = subprocess.run(prefix+args, input=text, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, '')
        piped = subprocess.run(prefix+['1', '--stdin'],
                               input=f.reader.D.demo_transaction()+'\r\n',
                               capture_output=True, text=True)
        self.assertEqual(piped.returncode, 0, piped.stderr)


if __name__ == '__main__':
    unittest.main()
