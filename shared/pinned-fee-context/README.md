# Pinned fee context

Inspect unsigned EIP-1559 fee caps using the base fee in an actual retained
Ethereum block, entirely offline. This joins Line 1's number-pinned ZTO snapshot
validator with Line 3's fee-context arithmetic and original-input decoder.
Copy this whole folder: all six unchanged runtime dependencies and a real dated
ZTO observation are ordinary files under it. Python 3.10+ standard library only.

Run from any directory to see it working:

```sh
python3 -B shared/pinned-fee-context/pinned_fee.py demo
```

Tried against the contributor's Ethereum relay at 2026-10-12T22:22:06Z:
block 26179285, hash
`0x44735faee05e859ee4521f1b5585c44450b7aaa8139a61ca0a2b1471c6b2adcc`,
base fee 218043369 wei per gas; real ZTO supply
1000000000000000000000000000 base units. The retained example is unchanged.
The unsigned ZTO totalSupply sample is synthetic inspection input, never signed,
sent or executed. At that recorded base fee its 2 gwei maximum and 1 gwei
priority caps yield an effective price of 1218043369 wei per gas. Native gas
is ETH even when the destination is ZTO. This is a historical diagnostic,
not a current quote or recommendation.

For supplied inputs, pipe one JSON object to `pinned_fee.py inspect`:

```json
{"snapshot": "replace with a pinned-zto-snapshot/1 object", "transaction": "original unsigned RLP hex or JSON text", "input_format": "rlp"}
```

The snapshot value must be the object, not a summary or filename; the transaction
must be the original text, not a precomputed summary. Use `input_format: "json"`
for an unsigned JSON-RPC transaction. Optional `expected_snapshot_sha256` is the
SHA-256 of sorted-key, compact, ASCII-escaped snapshot JSON with no newline.
Obtain an expected digest independently if authenticity matters. Both captured
blocks must contain the same canonical lowercase uint256 `baseFeePerGas`; the
entire pinned snapshot is validated before context is used. No missing fee,
chain, transaction field or signature is defaulted. Only mainnet snapshots fit.

Exit 0 means the fee checks passed; exit 1 retains a diagnostic for a fee cap
shortfall or invalid priority/cap order; exit 2 rejects malformed, inconsistent
or unsupported inputs with no partial JSON. Input and canonical output are each
bounded to 99,000 bytes; duplicate JSON keys and non-finite values are refused.
The report includes exact decimal integers, block identity, capture time,
provider endpoint, canonical content digest and original inspection text digest.
Neither digest is an Ethereum transaction hash.

Ten tests passed, including independent arithmetic, JSON/RLP equivalence,
missing/changed/oversized base fees, full snapshot validation, signed-input and
wrong-chain rejection, trusted digest checks, controlled CLI failures, fee
shortfalls, no-network operation and execution with no line folders nearby:

```sh
python3 -B shared/pinned-fee-context/test_pinned_fee.py
```

Recorded context is a provider observation. It establishes neither freshness,
finality, canonicality nor provider honesty. Validating the ZTO supply observation
does not authenticate another field of the block. A dishonest provider or a
consistent edit can pass local checks. Matching block fields before/after reads
can miss a reorg followed by its reversal. Fee arithmetic does not verify gas
sufficiency, execution, nonce, funds, inclusion or safety to sign. The supplied
unsigned message is not simulated by this tool. No network command, wallet,
secret, environment access, signing, transaction submission or payment exists.

`PROVENANCE.json` identifies every copied source and SHA-256. The gatherer's
checks and live evidence are retained under `gathering/checks/round-09/`.
