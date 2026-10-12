#!/usr/bin/env python3
"""Offline output-contract, scope and dependency checks for this gathering."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import subprocess
from make_thumbnail import png_rgb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'gathering/checks/round-09'


class Gallery(HTMLParser):
    def __init__(self):
        super().__init__();self.cards=0;self.scripts=0;self.sections=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='article':self.cards+=1
        if tag=='script':self.scripts+=1
        if tag=='section':self.sections.append(attrs.get('id'))


def jpeg_size(raw):
    assert raw[:2]==b'\xff\xd8' and raw[-2:]==b'\xff\xd9'
    pos=2
    while pos<len(raw):
        assert raw[pos]==255
        marker=raw[pos+1];length=int.from_bytes(raw[pos+2:pos+4],'big')
        if marker==0xc0:
            assert raw[pos+4]==8
            h,w=struct.unpack('>HH',raw[pos+5:pos+9]);return w,h
        assert marker!=0xda
        pos+=2+length
    raise AssertionError('no baseline JPEG dimensions')


def main():
    baseline=json.loads((OUT/'line-baseline.json').read_text())
    actual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for n in range(1,5) for p in (ROOT/f'line-{n}').rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}
    assert actual==baseline,'line folders changed'
    goals=json.loads((ROOT/'dist/goals.json').read_text())
    assert goals==[{'line':n,'goal':(ROOT/f'line-{n}/GOAL.md').read_text().strip()} for n in range(1,5)]
    record=json.loads((ROOT/'dist/gathering/08.json').read_text())
    assert set(record)=={'name','image','attributes'}
    assert [x['trait_type'] for x in record['attributes']]==['Cave','Wall','Number','Left behind','Meaning','One thing']
    values={x['trait_type']:x['value'] for x in record['attributes']}
    assert values['Cave']=='Base' and values['Wall']=='Gathering' and type(values['Number']) is int and values['Number']==8
    assert values['One thing']=='Gathering'
    raw=(ROOT/'artifacts/gathering/wall-v9.png').read_bytes()
    assert raw==(ROOT/'artifacts/gathering/wall.png').read_bytes()
    w,h,_=png_rgb(raw);assert (w,h)==(1254,1254)
    assert record['image']=='https://api.imd.fun/artifacts/'+hashlib.sha256(raw).hexdigest()
    thumb=(ROOT/'dist/gathering/08.jpg').read_bytes();assert jpeg_size(thumb)==(512,512) and len(thumb)<100000
    review=json.loads((OUT/'image-preservation.json').read_text())
    assert review['changed_pixels_outside_rectangle']==0 and review['changed_pixels']==4978
    gallery=Gallery();gallery.feed((ROOT/'dist/index.html').read_text())
    records=list((ROOT/'dist').glob('line-*/[0-9][0-9].json'))+list((ROOT/'dist/gathering').glob('[0-9][0-9].json'))
    assert gallery.cards==len(records)==133 and gallery.scripts==0
    assert gallery.sections==['line-1','line-2','line-3','line-4','gathering']
    for folder in ['line-1','line-2','line-3','line-4','gathering']:
        for i in range(2,22):assert (ROOT/f'dist/{folder}/{i:02d}.json').is_file()
    for mod in json.loads((ROOT/'shared/pinned-fee-context/PROVENANCE.json').read_text())['modules']:
        assert hashlib.sha256((ROOT/mod['source']).read_bytes()).hexdigest()==mod['sha256']
        assert (ROOT/'shared/pinned-fee-context'/mod['copy']).read_bytes()==(ROOT/mod['source']).read_bytes()
    modified=subprocess.run(['git','diff','--name-only'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    untracked=subprocess.run(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    changed=modified+untracked
    for name in changed:
        assert name.startswith(('gathering/','shared/','dist/','artifacts/gathering/','test/scratch/')),name
        p=ROOT/name
        if not name.startswith(('artifacts/','test/scratch/')) and p.is_file():assert p.stat().st_size<100000,name
    assert (ROOT/'gathering/COINS.md').read_text().startswith('none\n')
    for n in range(1,5):assert f'## Line {n}' in (ROOT/'gathering/REPORT.md').read_text()
    checks=json.loads((OUT/'tool-checks.json').read_text());assert all(x['exit']==0 for x in checks)
    report={'passed':True,'line_files_unchanged':len(actual),'line_suites':23,'line_tests':sum(x['tests_run'] for x in checks),'line_commands':len(checks),'shared_tests':10,'gallery_records':gallery.cards,'goal_count':len(goals),'png_dimensions':[w,h],'png_format':'RGB PNG','jpeg_dimensions':[512,512],'jpeg_format':'baseline JPEG','wall_sha256':hashlib.sha256(raw).hexdigest(),'scope_checked':changed,'unmet_visual_requirements':[],'visual_assessment':'manual; exact preservation outside patch checked in image-preservation.json'}
    (OUT/'deliverable.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='scope_checked'},indent=2))


if __name__=='__main__':main()
