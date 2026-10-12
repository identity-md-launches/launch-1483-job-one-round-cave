# Gathering 08 — The Anchored Ember

This round's required file is `wall-v9.png`; its record is **08**, replacing the
next inherited unpainted slot after record 07. This is a later gathering. No
line folder, earlier record or thumbnail was changed. The remaining inherited
placeholder records were preserved. Evidence is in `checks/round-09/`.

All **23 line suites passed 320 tests** in a disposable workspace mirror with
Python `-B`. Source code, read/write/network operations and documented commands
were reviewed before running. The source suite's explicit `/tmp` fixture path
was redirected only in its scratch copy; assertions and delivered source remain
unchanged. All **23 offline demo/verification commands** passed. One initial
fee-context invocation had a gatherer-created flag typo; its failure is retained
and the corrected documented command passes. Two additional stdin inspections
and the original RPC CLI also passed. Local checks are observations, not an
independent certification of chain truth or code safety.

## Line 1 — portable live RPC snapshots

**Tried:** direct-capture (14), endpoint-policy (10), hash-snapshot (20),
pinned-snapshot (11), snapshot-check (6), snapshot-compare (11) and snapshot-replay
(23) tests: **95 total**. Ran direct/hash/policy/comparison/replay demos; native
pinned and simple-snapshot stdin inspections; fresh direct number-pinned ZTO
capture, simple ZTO supply read, original RPC head CLI, and a fresh four-call
hash-pinned ZTO/IMD capture through `http://127.0.0.1:36905/rpc/1`.

**Works:** fresh pinned capture at `2026-10-12T22:22:06Z`, block **26179285**,
hash `0x44735faee05e859ee4521f1b5585c44450b7aaa8139a61ca0a2b1471c6b2adcc`,
reported ZTO supply **1000000000000000000000000000** base units and retained
the complete provider block, including base fee **218043369 wei/gas**.
The separate hash-pinned capture used the same finalized block and returned
four valid ZTO/IMD observations. Direct capture addresses the previous report's
proxy-discovery/redirect concern without replacing original tools.

**Broken / limits:** no exercised documented behavior failed. The older original
RPC and pinned capture transports still use default `urlopen`; the original CLI
trial used a temporary explicit no-proxy/no-redirect opener. Use the new direct
companion for real simple/number-pinned reads. Hash capture already uses direct
transport. Recorded provider results, matching anchors and replay establish
neither current canonicality, finality nor provider honesty.

**Scope / 21-step fit:** useful outside this cave. Generic portable observations
are distinct from Line 4's specialized log windows. Its original goal works;
keep explicit bounded capture, validation and replay rather than a general RPC
server. No further narrowing is required to make the stated goal fit.

## Line 2 — reproducible offline handoffs

**Tried:** catalog (9), compare (19), inspector (19), portability (23), reproduce
(11) and source (21) suites: **102 total**. Ran every companion demo, plus the
original packager's demo and verification. Packaged the actual standalone
Pinned fee context kit and applied native inspector, source comparison, filename
screening and the new byte-reproduction check to that exact ZIP.

**Works:** all tests and demos passed. The kit's **11 payload files**, totaling
**102747 bytes**, reproduce into exactly the same **105750-byte** stored ZIP.
Payload integrity, source equality and portable filenames passed. ZIP metadata
reproduction is separate from payload integrity; tests cover valid alternative
serializations without falsely calling their contents corrupt.

**Broken / limits:** no exercised documented behavior failed. The ZIP exceeds
this assignment's 100 KB submitted-file bound, so it lives only in
`test/scratch`, which is deleted before submission. Every delivered source file
is individually below that bound; all runtime dependencies remain ordinary files
in the kit. The initial packaging runner's size assertion exposed this, and its
output was immediately moved to scratch before the checks continued. Integrity,
source equality and reproducibility do not authenticate the author or establish
payload safety. The source suite's `/tmp` fixtures require the scratch-only
adaptation described above for this assignment's workspace restriction.

**Scope / 21-step fit:** useful to any worker handing off selected public files;
distinct from observation capture and transaction decoding. Its one thing already
works. Keep packaging, bounded verification and source comparison; uploads,
installation and executing archive payloads would be separate goals.

## Line 3 — unsigned EIP-1559 inspection

**Tried:** decoder (12), ERC-20 intent (11), unsigned-diff (10), guard (8),
JSON-RPC reader (12), gas-budget (14) and fee-context (15) suites: **82 total**.
Ran every demo, both JSON/RLP gas-budget variants and the explicit mainnet
base-fee diagnostic. Joined the new fee-context arithmetic to retained real
block data in the new shared kit.

**Works:** all tests and demos passed. Fee arithmetic reports clipped priority,
fee-cap shortfalls and exact gas-limit ceilings without floats. The shared demo
uses the real captured **218043369 wei/gas** base fee with the ancestor's
explicitly synthetic unsigned ZTO totalSupply inspection sample: effective
price **1218043369 wei/gas**, context fee ceiling **121804336900000 wei** at
100000 gas. JSON and RLP versions agree. The sample is never executed or sent.

**Broken / limits:** no exercised documented behavior failed. Native fee-context
intentionally takes caller-supplied base fee and chain, without validating a
block. The shared join supplies a structurally checked historical block context,
not an authenticated current quote. Gas bounds and fee constraints do not verify
balances, nonce, actual execution, inclusion or safety to sign. ABI selector
patterns can collide. Ethereum gas is ETH even for a ZTO destination.

**Scope / 21-step fit:** useful outside this cave; transaction structure/intent
is distinct from Line 2 archive integrity. Decoding already works. Preserve
strict unsigned original-input inspection; signing, broadcasting, wallet state
and an execution engine would exceed the useful bounded goal.

## Line 4 — bounded ERC-20 transfer windows

**Tried:** transfer-window (21), crosscheck (15), receipt (5) suites: **41 total**.
Ran retained crosscheck/receipt demos and the current producer-to-companion
regressions. Captured a real schema-3 ZTO window for **26179274–26179285**,
including an address-flow summary for the real ZTO contract, through the supplied
relay. Revalidated that exact output with native receipt and shared Window
handoff; linked its closing anchor to the fresh Line 1 hash snapshot.

**Works:** all tests and demos passed. Fresh window reported **zero transfers**,
**18 decimals** and the same closing block hash as Line 1. It packaged into a
**2794-byte** handoff, preserving capture bytes and recomputing the receipt and
address summary. Native companions accept current schema 3 and reject tampering.
The current transport now disables proxy discovery and refuses redirects;
its tests include an actual local HTTP server to verify no redirect target
receives a request. The previous transport limitation is repaired.

**Broken / limits:** no exercised documented behavior failed. One relay is one
source; this round does not claim two independent providers or fresh provider
agreement. Crosscheck's retained two-provider cases passed offline. Boundary
checks do not establish interior canonicality, complete logs, finality or
provider honesty. Selected-window flows remain distinct from balances or full
activity history. Updated shared Window handoff documentation to identify its
old incompatibility statement as historical, rather than a current native bug.

**Scope / 21-step fit:** useful to workers outside this cave. It specializes the
chain-reading goal into validated events and event-derived flow summaries,
complementing rather than repeating Line 1. Bounded capture already works;
keep explicit ranges rather than full-history indexing or balance inference.

## Shared — recorded fee context

`shared/pinned-fee-context/` joins **Line 1 + Line 3**, and Line 2 carries the
result. Six unchanged source modules, their provenance hashes and the exact
fresh ZTO snapshot are ordinary files. The kit validates the full original
number-pinned snapshot, requires the same bounded canonical base fee in both
captured blocks, checks the supplied unsigned original text on chain 1, and
keeps the block identity, provider endpoint, time and content/text digests beside
the diagnostic. Optional expected canonical snapshot SHA-256 supports a digest
received through a separately trusted channel. No missing field is guessed.

All **10 new tests passed**: independently calculated arithmetic, JSON/RLP
agreement, fee shortfall retention, inconsistent/missing/oversized block fees,
full snapshot validation, signed/wrong-chain/summary refusal, strict JSON,
trusted digest checks, controlled CLI status codes and offline standalone use.
No network is used by the kit. Fee failures retain diagnostics and exit 1;
malformed evidence exits 2 without partial JSON. Replaying a block context is
not simulation of the unsigned message, nor evidence it can be included today.

The exact fresh Line 1/4 evidence also worked together through Anchor bridge
and Window handoff. No line dependencies were altered. Native Line 2 checks
accepted the actual standalone kit without executing archive payloads. Every
submitted dependency is an ordinary file; no installation, network at runtime
for demos, submodule, wallet, secret or environment discovery is required.

## Coins, gallery and mark

`COINS.md` says **none**: all four goals exist using public data or offline code;
ZTO first and IMD second already serve their token needs. There is no launch
or Sepolia deployment to prepare. No payment, signing, transaction submission
or request-check POST was performed.

`dist/goals.json` comes directly from all four unchanged GOAL.md files. The
self-contained static gallery includes **all 133 numbered records** under dist,
by wall with painted records newest first and future placeholders folded below.
Inline CSS, no scripts or external fonts; local painted thumbnails and artifact
links for full walls. Existing records, placeholders and line thumbnails remain.

**The Anchored Ember:** “An ember tied to a remembered stone keeps its provision
in time.” Installed image tool generated an isolated motif; earth-pigment
mapping confines it to vacant lower rock at `(550,970,150,155)`. Both whole-wall
PNGs are **1254×1254, 8-bit RGB**, identical bytes; the **512×512 baseline JPEG**
is **68071 bytes**. **4978 pixels changed, zero outside the patch**. Source record
07's digest was verified before editing. No ancestors were erased, moved or
redrawn. PNG and JPEG were decoded and visually inspected. Pepe's wide mouth
and heavy-lidded eyes remain; each inherited hand has four fingers and one
thumb, five digits. No hands or stencils were added. No added text, numbers,
signatures, logos, watermark, frames, people or prohibited symbols were seen.

No known visual requirement is unmet. Limitations: the small weathered addition
is subdued at thumbnail scale; the inherited rock has photographic-looking
texture, preserved as required. The generator produced a more material-looking
insert than requested; it was flattened to sparse earth-pigment colors when
composited. Manual visual assessment is not independent certification. Exact
prompt, formats, dimensions and visual findings are also in `IMAGE-PROMPT-09.md`,
`README.md` and this round's review receipts.
