# Window handoff

Carry an ERC-20 transfer observation to another worker in a deterministic,
offline-verifiable HANDOFF v1 ZIP. This joins Line 4's raw-log validation and
receipts with Line 2's packaging, streaming inspection and filename screening.
Python 3.10+ and the standard library suffice. Copy this entire folder to use
it independently: no line folders, network or installation are needed.

One command from the repository root shows it working:

```sh
python3 -B shared/window-handoff/window_handoff.py demo
```

Tried locally: exact retained PublicNode ZTO evidence for blocks
26177298–26177309, three transfers, packaged and verified in memory.
Repeated packaging produced identical 6,109-byte ZIPs, SHA-256
`67ca32dc3aa2e6307738487f0d25f6a3e9ecf76f83952b7a85940978ee99bb67`.
Original capture bytes, archive hashes/CRCs and the recomputed receipt all
matched. This is dated provider evidence, not current state or a balance.

## Current producer compatibility

At Gathering 06, Line 4's capture emitted **schema 3**, while its native crosscheck and
receipt still required schema 2. The native companions were repaired in the
following round and pass current Gathering 08 checks. This copied validator accepts both versions,
retaining all inherited chain/token/range/anchor/raw-log/count checks.
Optional schema-3 address summaries are recomputed; false values, JSON type
substitutions and malformed addresses are rejected. No line folder changed.

Fresh public reads through PublicNode and dRPC at
2026-10-12T19:54:47Z–19:54:48Z both returned schema-3 ZTO windows for
26178550–26178551 with zero reported transfers. Native receipts and crosscheck
rejected these outputs. This kit successfully packaged and replayed the exact
captures in 2,366 and 2,351 bytes, and its copied crosscheck reported agreement.
The gathering's trial transport disabled proxy discovery and redirects.
Exact evidence and trial results are in `gathering/checks/round-07/`.
The kit itself has **no network command**.

## Use

Package an existing public capture into a fresh workspace filename:

```sh
python3 -B shared/window-handoff/window_handoff.py pack gathering/checks/round-07/live-window-1.json test/scratch/window.zip
python3 -B shared/window-handoff/window_handoff.py inspect test/scratch/window.zip
```

Create the destination's parent first. ZIP payloads are exactly
`evidence/transfer-window.json` and `evidence/window-receipt.json`, plus the
standard `HANDOFF.json` manifest. Line 2's original inspectors also verify
the archive. Integrity checks run **before** evidence parsing; the saved
receipt is then recomputed from validated raw logs. A rehashed ZIP containing
a false receipt fails. Original capture bytes are preserved exactly.

Use `inspect --sha256 DIGEST` when a trusted archive digest arrived
independently. Exit 0 means checks completed, exit 1 refuses unsupported,
invalid or inconsistent inputs with no partial success JSON, and syntax
errors exit 2. Paths must be relative to the current workspace without `..`
or symlinks. Existing outputs are never overwritten. Each file and the whole
archive are capped at 99,000 bytes; manifest and ZIP metadata each at 4,096
bytes; payload count at two. Oversized captures fail rather than truncate.
Archives are never extracted and their contents are never executed.

`window_sha256` identifies the validated semantic window, ignoring duplicate
log delivery/order. `capture_sha256` fingerprints canonical JSON of the full
capture; `capture_bytes_sha256` identifies original bytes including whitespace.
Integrity without an independent digest does not authenticate a sender or
provider: content and checksums can be replaced together. Neither receipts nor
agreement prove completeness, finality, independence, balances or execution
safety. Conservative filename screening does not promise OS extraction or
software portability. Stable ancestor paths are assumed; this is not an OS
sandbox or a secret scanner. Package explicitly selected public evidence.

No environment settings, configuration, wallets, keys or secrets are read.
No signing, sending, payments, posting or deployment are implemented.

## Checks and provenance

```sh
python3 -B shared/window-handoff/test_window_handoff.py
```

All 12 behavioral checks passed: exact bytes/determinism, current producer
schema-3 replay, address-summary validation, malformed evidence, removed logs,
duplicate delivery, rehashed false receipts, CRC-repaired tampering, trusted
digests, unexpected payloads, strict JSON/bounds, and CLI roundtrip/overwrite
refusal. The demo also passed after copying only this folder into scratch.

`PROVENANCE.json` records six original and copied module hashes. Only two
adaptations were made: the crosscheck's accepted schema versions, and the
portability module's fixed standalone dependency location. The retained demo
capture was copied byte for byte from
`line-4/tools/transfer-crosscheck/publicnode.json`.
