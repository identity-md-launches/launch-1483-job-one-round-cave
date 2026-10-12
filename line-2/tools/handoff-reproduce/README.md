# Handoff Reproduce

Check whether a verified workspace HANDOFF v1 ZIP is exactly reproducible by
the original deterministic packager. Python 3.8+ and only its standard library
are needed. From the workspace root, run:

```sh
python3 -B line-2/tools/handoff-reproduce/reproduce.py demo
```

When tried, the actual inherited `line-2/handoff.zip` reproduced byte for byte:
2 payload files, 12,603 payload bytes, 13,181 archive bytes, SHA-256
`aaa03a258268263186f610e17ad8ede6851c8597b70a7ec29ae6b283f72f60bb`.
The demo reads the real archive and writes nothing. Its self-computed digest
identifies those bytes; it does not authenticate their sender.

For another archive:

```sh
python3 -B line-2/tools/handoff-reproduce/reproduce.py check line-2/handoff-inspect.zip
```

Optional `--sha256 HASH` checks a digest obtained independently. Exit 0 means
valid and byte reproducible; exit 2 means valid payload integrity but different
archive serialization; exit 1 refuses invalid inputs, with no JSON on stdout.
JSON records both archive hashes and lengths, file and payload counts, and the
first differing zero-based byte offset (`null` on equality). The tool neither
changes the supplied ZIP nor saves the rebuilt ZIP.

The bounded inspector validates the entire immutable archive snapshot before
any rebuild. The original writer reconstructs the canonical manifest and ZIP
in memory from those verified payload bytes, and the inspector checks the
rebuild too. Canonical v1 uses sorted paths, compact sorted-key manifest JSON
plus newline, stored entries, a fixed 1980 timestamp, Unix regular-file 0644
attributes, and no archive comments. Valid alternative timestamps, file modes,
entry order, JSON whitespace or comments therefore yield exit 2. Such a result
does not mean the payload is corrupt. The exact writer profile is named in JSON;
this is a check of the supplied payload against that profile, not proof that
the worker's original source, build process or dependencies were reproducible.
Use the existing source-check tool for workspace equality.

Keep these unchanged runtime dependencies at their workspace paths when moving
this piece: `line-2/tools/handoff/handoff.py` and
`line-2/tools/handoff-inspect/inspect_handoff.py`. The demo additionally needs
`line-2/handoff.zip`. Imports load these trusted local tool modules, never ZIP
payload modules. Run from the workspace root.

Reads are limited to relative workspace paths without `..` or symlinks, regular
files only. Input defaults are at most 66 MiB archive, 64 MiB payload, 1,000
files and 512 KiB each of manifest and central-directory metadata. The original
writer also enforces its existing bounds. In-memory reconstruction can require
several times the archive size in RAM; the entire operation is bounded, but is
not a streaming-memory verifier. ZIP64, compression and data descriptors are
outside the inherited format. Integrity and reproducibility prove neither
authorship nor safe or functional code. No extraction, payload execution,
network, environment-variable reads, keys, wallets, signing, sending, uploads,
payments or dependency installation are used.

Behavior checks:

```sh
python3 -B line-2/tools/handoff-reproduce/test_reproduce.py
```

All 11 tests passed, including the inherited archive, Unicode/nested/empty
payloads, five valid serialization variations, corruption, malformed ZIPs,
trusted digests, archive/payload limits, CLI exit codes and workspace-path
refusals. CLI fixtures live only in `test/scratch`; no payload is executed.
