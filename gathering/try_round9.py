#!/usr/bin/env python3
"""Exercise live evidence interoperability and native handoff checks read-only."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'gathering/checks/round-09'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod


def save(name,obj):
    raw=json.dumps(obj,indent=2)+'\n'
    assert len(raw.encode())<100000
    (OUT/name).write_text(raw)


def main():
    bridge=load('round9_bridge','shared/anchor-bridge/anchor_bridge.py')
    snapshot=load('round9_snapshot','line-1/tools/hash-snapshot/hash_snapshot.py')
    receipt=load('round9_receipt','line-4/tools/transfer-window-receipt/receipt.py')
    kit=load('round9_window_kit','shared/window-handoff/window_handoff.py')
    obj=json.loads((OUT/'live-hash-zto-imd.json').read_text())
    window=json.loads((OUT/'live-window-zto.json').read_text())
    save('live-snapshot-inspection.json',snapshot.inspect(obj))
    save('live-window-receipt.json',receipt.receipt(window))
    save('live-anchor-link.json',bridge.link(obj,window))
    archive=kit.build((OUT/'live-window-zto.json').read_bytes())
    assert len(archive)<100000
    (OUT/'live-window.zip').write_bytes(archive)
    save('live-window-handoff.json',kit.inspect_bytes(archive))
    # Test the original readers through the current direct public-read transport;
    # leave their sources unchanged and refuse environment proxy discovery.
    direct=load('round9_direct','line-1/tools/direct-capture/direct_capture.py')
    endpoint='http://127.0.0.1:36905/rpc/1'
    save('live-simple-zto.json',direct.capture(endpoint,'eth_call',[direct.pinned.CALL,'latest']))
    trials=[]
    commands=[['line-1/tools/pinned-snapshot/pinned_snapshot.py','inspect'],
              ['line-1/tools/snapshot-check/check_snapshot.py']]
    inputs=[(OUT/'live-pinned-zto.json').read_text(),(OUT/'live-simple-zto.json').read_text()]
    for command,text in zip(commands,inputs):
        run=subprocess.run(['python3','-B',*command],cwd=ROOT,input=text,text=True,capture_output=True,timeout=30)
        trials.append({'command':command,'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr})
    save('extra-inspections.json',trials)
    assert all(x['exit']==0 for x in trials)
    print(json.dumps({'snapshot_block':int(obj['anchor']['number'],16),'window':[window['from_block'],window['to_block']],'transfers':window['transfer_count'],'archive_bytes':len(archive)},indent=2))


if __name__=='__main__':main()
