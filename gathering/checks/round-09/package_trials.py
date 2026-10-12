"""Exercise reviewed native Line 2 packaging on the actual standalone kit."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'gathering/checks/round-09'
commands=[
 ['line-2/tools/handoff/handoff.py','pack','shared/pinned-fee-context','test/scratch/pinned-fee-context.zip'],
 ['line-2/tools/handoff-inspect/inspect_handoff.py','inspect','test/scratch/pinned-fee-context.zip'],
 ['line-2/tools/handoff-source/source_check.py','check','test/scratch/pinned-fee-context.zip','shared/pinned-fee-context'],
 ['line-2/tools/handoff-portability/portability.py','check','test/scratch/pinned-fee-context.zip'],
 ['line-2/tools/handoff-reproduce/reproduce.py','check','test/scratch/pinned-fee-context.zip'],
]
for i,args in enumerate(commands,1):
 r=subprocess.run(['python3','-B',*args],cwd=ROOT,text=True,capture_output=True,timeout=60)
 (OUT/f'package-{i:02d}.json').write_text(json.dumps({'command':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
 print(i,r.returncode,r.stderr)
 assert r.returncode==0
 assert all(p.stat().st_size<100000 for p in OUT.iterdir() if p.is_file())
