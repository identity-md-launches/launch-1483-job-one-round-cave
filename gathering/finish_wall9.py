#!/usr/bin/env python3
"""Transfer generated earth pigment into vacant rock, preserving ancestor pixels."""
import hashlib
import json
from pathlib import Path
from make_thumbnail import png_rgb, resize, jpeg
from finish_wall8 import encode_png

SOURCE_SHA='846767d546efffd0fe4f223989c803aaafcb52e8c629b5528140be2dc380a5d5'
RECT=(550,970,150,155)


def main():
    source=Path('artifacts/gathering/wall.png').read_bytes()
    assert hashlib.sha256(source).hexdigest()==SOURCE_SHA
    w,h,old=png_rgb(source)
    iw,ih,insert=png_rgb(Path('artifacts/gathering/wall-v9.png').read_bytes())
    assert (w,h)==(1254,1254)
    points=[(x,y) for y,row in enumerate(insert) for x in range(iw) if min(row[3*x:3*x+3])<160]
    x0,x1=min(x for x,y in points)-2,max(x for x,y in points)+3
    y0,y1=min(y for x,y in points)-2,max(y for x,y in points)+3
    result=[bytearray(row) for row in old]
    left,top,rw,rh=RECT
    for y in range(top,top+rh):
        for x in range(left,left+rw):
            sx=x0+(x-left)*(x1-x0)//rw;sy=y0+(y-top)*(y1-y0)//rh
            r,g,b=insert[sy][sx*3:sx*3+3]
            if min(r,g,b)>210:continue
            alpha=min(.70,(210-min(r,g,b))/210*.70)
            pigment=(151,93,28) if r>g and g>b*1.7 and g>110 else ((130,49,24) if r>g*1.35 and r>65 else (31,24,17))
            i=x*3
            result[y][i:i+3]=bytes(round(a*(1-alpha)+b*alpha) for a,b in zip(old[y][i:i+3],pigment))
    changed=outside=0
    for y in range(h):
        for x in range(w):
            if old[y][x*3:x*3+3]!=result[y][x*3:x*3+3]:
                changed+=1;outside+=not(left<=x<left+rw and top<=y<top+rh)
    assert changed>300 and outside==0
    wall=encode_png(w,h,result);preview=jpeg(resize(w,h,result));assert len(preview)<100000
    Path('artifacts/gathering/wall-v9.png').write_bytes(wall)
    Path('artifacts/gathering/wall.png').write_bytes(wall)
    Path('dist/gathering/08.jpg').write_bytes(preview)
    review={'source_record':7,'record_number':8,'source_sha256':SOURCE_SHA,'wall_sha256':hashlib.sha256(wall).hexdigest(),'png_dimensions':[w,h],'png_format':'8-bit RGB PNG','png_bytes':len(wall),'generated_insert_dimensions':[iw,ih],'jpeg_dimensions':[512,512],'jpeg_format':'baseline JPEG','jpeg_bytes':len(preview),'addition_rectangle':list(RECT),'changed_pixels':changed,'changed_pixels_outside_rectangle':outside,'method':'Installed image tool pigment insert, mapped to earth pigments and confined in memory to vacant lower rock.'}
    Path('gathering/checks/round-09/image-preservation.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(review,indent=2))


if __name__=='__main__':main()
