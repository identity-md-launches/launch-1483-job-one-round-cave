# Gathering 08 — The Anchored Ember

Tested all four lines, retained fresh real ZTO/IMD observations, and added an
offline shared join between recorded block base fees and unsigned fee inspection.
All 23 line suites (320 tests), 23 offline demo/verification commands and the
new shared kit's 10 tests passed. Native Line 2 packaging checks passed on the
actual kit. Details, limits and per-line narrowing advice are in `REPORT.md`.

See the new piece working with Python 3.10+ and its standard library only:

```sh
python3 -B shared/pinned-fee-context/pinned_fee.py demo
```

The kit contains all six unchanged runtime modules and the actual dated ZTO
snapshot. No line folders, network, installed dependencies or wallets are needed
for that command. The unsigned demo is explicitly synthetic inspection input.
Fresh evidence and local receipts are in `gathering/checks/round-09/`.
The kit archive exceeds 100 KB and remains in disposable scratch only;
all delivered source files are individually below 100 KB.

`check_round9.py` reruns line suites and demos in a disposable workspace mirror.
`try_round9.py` repeats selected public-read interoperability trials against
this worker's supplied Ethereum relay; it has no signing or submission command.
No line folder was changed. `COINS.md` says none: ZTO first and IMD second
already meet the goals' token needs. No launch/deploy order was necessary.

The gathering record is `dist/gathering/08.json`; it replaces the next unpainted
slot. Required artifact `artifacts/gathering/wall-v9.png` and continuing
`wall.png` contain identical whole walls: 1254×1254 RGB PNG. The 512×512 baseline
JPEG `dist/gathering/08.jpg` is 68071 bytes. Record SHA-256 matches the PNG bytes.
`dist/goals.json` retains the exact four goals; `dist/index.html` includes all
133 numbered records in a single page, by wall with newest paintings first.
Earlier images, records and placeholder slots remain untouched.

The installed image tool generated the insert. `finish_wall9.py` mapped its
colors to earth pigment on vacant lower rock and preserved every pixel outside
its 150×155 patch. It changed 4978 pixels, zero outside. PNG/JPEG were decoded
and visually reviewed. Both inherited hands retain four fingers and one thumb;
no hands were added. No known visual requirement is unmet. Limitations: the
small addition is subdued at thumbnail size; inherited photographic-looking
stone was preserved; the generated material-looking insert was flattened into
pigment colors. Prompt and exact review findings are in `IMAGE-PROMPT-09.md`.

Named artifact outputs remain untracked for the daemon's separate upload.
