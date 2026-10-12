#!/usr/bin/env python3
"""Evidence-context regressions over a real retained ZTO capture."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
import pinned_fee as tool


class Tests(unittest.TestCase):
    def setUp(self):
        self.obj = tool.demo_input()

    def test_real_block_context_and_independent_fee_arithmetic(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')):
            result = tool.inspect(self.obj)
        base = int(self.obj['snapshot']['block']['baseFeePerGas'], 16)
        fees = result['fee_diagnostic']['fees']
        self.assertEqual(int(fees['effectiveGasPriceWei']), min(2000000000, base+1000000000))
        self.assertEqual(int(fees['contextFeeCeilingAtGasLimitWei']), 100000*min(2000000000, base+1000000000))
        self.assertFalse(result['transaction_execution_verified'])
        self.assertEqual(result['snapshot']['block_hash'], self.obj['snapshot']['block']['hash'])
        self.assertEqual(result['snapshot']['token'], tool.fee.reader.D.ZTO)

    def test_rlp_json_equivalence(self):
        a = tool.inspect(self.obj)
        self.obj.update(transaction=json.dumps(tool.fee.reader.demo_object()), input_format='json')
        b = tool.inspect(self.obj)
        self.assertEqual(a['fee_diagnostic']['fees'], b['fee_diagnostic']['fees'])
        self.assertEqual(a['fee_diagnostic']['inspection'], b['fee_diagnostic']['inspection'])

    def test_fee_shortfall_retains_diagnostic(self):
        tx = tool.fee.reader.demo_object()
        tx.update(maxFeePerGas='0x1', maxPriorityFeePerGas='0x0')
        self.obj.update(transaction=json.dumps(tx), input_format='json')
        result = tool.inspect(self.obj)
        self.assertFalse(result['fee_diagnostic']['passesCheckedFeeConstraints'])
        self.assertIsNone(result['fee_diagnostic']['fees']['effectiveGasPriceWei'])

    def test_block_fee_required_canonical_bounded_and_consistent(self):
        for bad in (None, True, 1, '0x00', '0x01', '0xA', '0x'+'1'*65, '1'):
            obj = copy.deepcopy(self.obj)
            for k in ('block','block_after'):obj['snapshot'][k]['baseFeePerGas']=bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):tool.inspect(obj)
        obj = copy.deepcopy(self.obj)
        del obj['snapshot']['block']['baseFeePerGas']
        with self.assertRaises(ValueError):tool.inspect(obj)
        obj = copy.deepcopy(self.obj)
        obj['snapshot']['block_after']['baseFeePerGas']='0x0'
        with self.assertRaises(ValueError):tool.inspect(obj)

    def test_snapshot_validated_before_fee_context(self):
        for change in ('chain','call','anchor','supply'):
            obj = copy.deepcopy(self.obj)
            s = obj['snapshot']
            if change=='chain':s['chain_id']='0x2'
            if change=='call':s['params'][0]['to']=tool.fee.reader.intent.IMD
            if change=='anchor':s['block_after']['hash']=s['block']['parentHash']
            if change=='supply':s['result']='0x1'
            with self.subTest(change=change), self.assertRaises(ValueError):tool.inspect(obj)

    def test_trusted_digest_optional_and_exact(self):
        self.obj['expected_snapshot_sha256']=hashlib.sha256(tool.canonical(self.obj['snapshot'])).hexdigest()
        self.assertTrue(tool.inspect(self.obj)['snapshot']['expected_digest_matched'])
        for bad in ('',True,'f'*64):
            self.obj['expected_snapshot_sha256']=bad
            with self.assertRaises(ValueError):tool.inspect(self.obj)

    def test_chain_mismatch_signed_or_summary_input_rejected(self):
        for mutation in ('chainId','r','from'):
            tx=tool.fee.reader.demo_object()
            tx[mutation]='0x2' if mutation=='chainId' else '0x1'
            self.obj.update(transaction=json.dumps(tx),input_format='json')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):tool.inspect(self.obj)
        self.obj.update(transaction='{"inspection":{}}',input_format='json')
        with self.assertRaises(ValueError):tool.inspect(self.obj)

    def test_strict_input_bounds_duplicate_keys_and_unknown_fields(self):
        for raw in (b'{"snapshot":{},"snapshot":{}}',b'NaN',b'\xff',b'x'*99001):
            with self.assertRaises((ValueError,UnicodeError)):tool.parse(raw)
        for obj in (None,[],{},dict(self.obj,extra=True)):
            with self.assertRaises(ValueError):tool.inspect(obj)

    def test_cli_exit_codes_no_partial_error_output_and_offline_demo(self):
        for obj,status in ((self.obj,0),({},2)):
            out,err=io.StringIO(),io.StringIO()
            stdin=io.TextIOWrapper(io.BytesIO(json.dumps(obj).encode()))
            with patch.object(sys,'stdin',stdin),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err),patch.object(socket,'socket',side_effect=AssertionError('network')):
                self.assertEqual(tool.main(['inspect']),status)
            self.assertEqual(bool(out.getvalue()),status==0)
        tx=tool.fee.reader.demo_object();tx.update(maxFeePerGas='0x0',maxPriorityFeePerGas='0x0')
        self.obj.update(transaction=json.dumps(tx),input_format='json')
        with patch.object(sys,'stdin',io.TextIOWrapper(io.BytesIO(json.dumps(self.obj).encode()))),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main(['inspect']),1)
        out=io.StringIO()
        with patch.object(socket,'socket',side_effect=AssertionError('network')),contextlib.redirect_stdout(out):
            self.assertEqual(tool.main(['demo']),0)
        self.assertIn('synthetic',json.loads(out.getvalue())['demo'])

    def test_kit_without_line_folders(self):
        result=subprocess.run([sys.executable,'-B',str(Path(tool.__file__).resolve()),'demo'],cwd=Path(tool.__file__).resolve().parent,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['offline'])


if __name__=='__main__':unittest.main(verbosity=2)
