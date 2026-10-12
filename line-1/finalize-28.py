#!/usr/bin/env python3
"""Confine generated pigment; finalize round 28 records and required preview.

Run only before wall.png has been overwritten: wall.png is record 27, wall-v9.png
is the image-tool edit. Re-running after finalization deliberately fails the hash
check. Uses only the already reviewed gathering PNG/JPEG format helpers.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import zlib

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('thumbnail', root / 'gathering/make_thumbnail.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
old_path = root / 'artifacts/line-1/wall.png'
new_path = root / 'artifacts/line-1/wall-v9.png'
old = old_path.read_bytes()
previous = json.loads((root / 'dist/line-1/27.json').read_text())
assert hashlib.sha256(old).hexdigest() == previous['image'].rsplit('/', 1)[1]
w, h, ancestors = helper.png_rgb(old)
w2, h2, generated = helper.png_rgb(new_path.read_bytes())
assert (w, h) == (w2, h2) == (1254, 1254)
# Only new charcoal/red pigment within vacant rock. Never copy the background.
box = (915, 345, 1050, 442)
rows = [bytearray(row) for row in ancestors]
changed = 0
for y in range(box[1], box[3]):
    for x in range(box[0], box[2]):
        at = x * 3
        source = generated[y][at:at+3]
        before = ancestors[y][at:at+3]
        r, g, b = source
        dark_pigment = r < 115 and g < 80 and b < 60
        substantially_darker = sum(before) - sum(source) > 90
        red_pigment = (960 <= x < 1020 and 346 <= y < 398 and
                       75 < r < 165 and g < 85 and b < 55 and r > 1.85 * g and
                       r - g > before[0] - before[1] + 15 and
                       sum(abs(a - b) for a, b in zip(source, before)) > 40)
        if (dark_pigment and substantially_darker) or red_pigment:
            rows[y][at:at+3] = source
            changed += 1
assert changed > 500, changed
outside = 0
for y in range(h):
    for x in range(w):
        different = rows[y][x*3:x*3+3] != ancestors[y][x*3:x*3+3]
        if different and not (box[0] <= x < box[2] and box[1] <= y < box[3]):
            outside += 1
assert outside == 0


def chunk(tag, body):
    return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body))


png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(b''.join(b'\0' + bytes(row) for row in rows), 9))
       + chunk(b'IEND', b''))
assert helper.png_rgb(png)[2] == [bytes(row) for row in rows]
new_path.write_bytes(png)
old_path.write_bytes(png)
jpg = helper.jpeg(helper.resize(w, h, rows))
assert len(jpg) < 100000
(root / 'dist/line-1/28.jpg').write_bytes(jpg)
sha = hashlib.sha256(png).hexdigest()
meaning = 'A narrow charcoal bowl carries one ochre pebble directly across the rock.'
record = {'name': 'The Direct Vessel', 'image': 'https://api.imd.fun/artifacts/' + sha,
          'attributes': [{'trait_type': key, 'value': value} for key, value in [
              ('Cave', 'Base'), ('Wall', 'Line 1'), ('Number', 28),
              ('Left behind', 'direct-capture'), ('Meaning', meaning),
              ('One thing', 'portable live Ethereum state snapshots')]]}
(root / 'dist/line-1/28.json').write_text(json.dumps(record, indent=2) + '\n')
review = {'round': 28, 'name': record['name'], 'meaning': meaning,
          'source_sha256': hashlib.sha256(old).hexdigest(), 'wall_sha256': sha,
          'wall': {'paths': ['artifacts/line-1/wall-v9.png', 'artifacts/line-1/wall.png'],
                   'format': 'PNG', 'width': w, 'height': h, 'bit_depth': 8, 'color': 'RGB',
                   'bytes': len(png)},
          'preview': {'path': 'dist/line-1/28.jpg', 'format': 'baseline JPEG',
                      'width': 512, 'height': 512, 'bytes': len(jpg)},
          'preservation': {'pigment_box_xyxy': box, 'changed_pixels': changed,
                           'changed_pixels_outside_box': outside,
                           'all_existing_motifs_outside_box': True},
          'visual_review': {'status': 'pending final inspection',
                            'hands_added': 0, 'unmet_requirements': []}}
(root / 'line-1/wall-review-28.json').write_text(json.dumps(review, indent=2) + '\n')
print(json.dumps(review, indent=2))
