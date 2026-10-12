# Explain unsigned EIP-1559 fees against a supplied base fee

`fee_context.py` reads the **original unsigned transaction**, either canonical
nine-field type-2 RLP or a complete unsigned JSON-RPC object. It preserves the
inherited transaction summary and ZTO/IMD destination interpretation, then
explains how much of the priority fee fits under the maximum fee at an explicitly
supplied base fee. The caller must supply the context chain ID; a mismatch is
rejected before any fee report is produced.

One command from the repository root shows it working without network access:

```sh
python3 -B line-3/tools/fee-context/fee_context.py --context-chain 1 --base-fee-wei 1000000000 --demo
```

Tried locally: exit 0, ZTO on Ethereum, `totalSupply()` ABI-pattern match,
1,000,000,000 wei/gas base fee, 1,000,000,000 effective priority fee,
2,000,000,000 effective gas price, and a 200,000,000,000,000 wei ceiling at
the supplied 100,000 gas limit. **Both the transaction and the supplied base fee
in this demonstration are synthetic, not a captured block or live quote.**
The destination is the actual ZTO contract
`0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`. Mainnet gas is paid in ETH;
a ZTO call does not change that protocol requirement.

## Inputs and output

Use `--transaction '0x02...'` or `--stdin` instead of `--demo`. Add
`--format json` for a complete JSON-RPC transaction object. RLP stdin allows one
trailing LF or CRLF. All transaction inputs remain bounded by the inherited
512-Ki-character, 128-KiB envelope and RLP depth/item limits. JSON requires all
fields, permits exactly one of `data`/`input`, and rejects duplicate keys,
signatures, sender fields and unknown metadata. This tool never accepts a claimed
decoded summary as evidence.

`--base-fee-wei` and `--context-chain` use canonical decimal integers: no units,
floats, exponents, signs or leading zeroes. Base fee can be zero. Context chain
must be positive. All six transaction integer fields and context values must
fit uint256. Products are exact Python integers and may exceed uint256; they
are arithmetic totals, not serialized EVM fields. No input files, environment
variables, keys, wallets, network, signing, sending, payment or posting are used.

The standard-library-only tool depends on the unchanged ordinary sibling files
in `rpc-unsigned-reader`, `erc20-intent`, and `zto-eip1559-decoder`. Keep these
folders together; no installation is required. An absolute script path also
works from another current directory.

For fee cap `C`, priority cap `P`, supplied base fee `B` and gas limit `G`:

- `P > C` and `B > C` are independent checked violations.
- When both checks pass, effective priority is `min(P, C-B)` and effective
  price is `B + min(P, C-B)`.
- Full priority remains available through base fee `C-P`, inclusive. Fee-cap
  coverage alone remains possible through base fee `C`, inclusive, with zero
  priority at that boundary.
- `G*C` is the transaction fee ceiling. `G*effectivePrice` is the ceiling at
  this supplied context. Separate burn and priority ceilings sum to that
  contextual ceiling. Native transaction value is added only to the maximum
  fee ceiling, separately from any token amount embedded in calldata.

Output schema is `fee-context/v1`, with exact integer quantities represented as
decimal strings. When a fee constraint fails, effective prices and contextual
ceilings are **null**, never clamped into apparently valid fees. Exit 0 means
only the fee checks passed; exit 1 emits a complete report of failed fee checks;
exit 2 means malformed, ambiguous, signed, unsupported, oversized or mismatched
input, with no partial JSON. CLI usage errors also return 2.

The rules were checked against the primary
[EIP-1559 specification](https://eips.ethereum.org/EIPS/eip-1559).
The caller must establish that those rules apply to the supplied chain/block.
No block, source, freshness, balance, nonce, inclusion, execution, intrinsic gas,
block limits, actual gas used, refunds or safety to sign is verified. A zero-gas
message can pass these fee-only checks; use the separate `gas-budget` tool for
explicit-profile intrinsic-gas diagnostics. A sufficient fee cap does not prove
transaction validity or inclusion. Destination and selector labels remain
pattern matches, not proof of contract behavior.

## Checks tried

```sh
python3 -B line-3/tools/fee-context/test_fee_context.py
```

All 15 tests passed, covering full/clipped/zero priority, cap equality and
one-wei shortfall, both violations, chain mismatch, exact uint256 products,
canonical decimal validation, original JSON/RLP equivalence, signed and
ambiguous inputs, size limits, 150 independently calculated seeded cases,
and CLI stdin/exit/no-partial-output behavior. No chain request was made.
Local checks do not independently certify chain facts.

## Round 28 wall

**Pepe Shelters the Provision**: “Pepe shelters two heaps of provision beneath
an ochre arch.” The installed image tool edited the inherited wall. The renderer
placed the motif lower than requested; the final confined composition retains
its actual vacant-stone rectangle `(809, 1025, 148, 90)` with a seven-pixel edge
fade. All pixels outside it, including all ancestral paintings, are exactly
unchanged. There are 12,750 changed pixels inside and zero outside.

Delivered `artifacts/line-3/wall-v9.png` and identical continuing `wall.png`:
1254×1254 opaque RGB PNGs. `dist/line-3/28.jpg` is a 512×512 baseline JPEG,
74,254 bytes. `dist/line-3/28.json` links the final PNG's SHA-256.
`line-3/round-28-review.json` records dimensions, formats, checks and visual
requirements. The two PNG outputs remain untracked for separate upload.

The final PNG and JPEG were visually inspected: inherited heavy-lidded Pepe,
wide mouth and two five-digit hands remain. No new hands or hand stencils were
added. The new arch and pebbles are worn earth-pigment strokes on bare stone.
No letters, numbers, captions, signatures, logos, watermarks, new borders or
frames, real people, political/hateful symbols or 3D effects were found.
No visual acceptance requirement is knowingly unmet. The motif is small and
subdued in the thumbnail. Local review is not independent artistic certification.

Final prompt for the installed image tool's edit mode:
Use case: precise-object-edit. This is an edit target, an ancestral cave painting. Preserve exact square size, rock, cracks, colour, torchlight, framing and every existing pigment mark. Add only a SMALL worn earth-pigment drawing on empty lower-right stone, entirely within x=960..1100 y=900..1020 of the 1254x1254 image: a low red ochre arched shelter over two little heaps of charcoal pebbles, one heap larger and one smaller. The shelter represents a limit to a traveller's provision. Very simple uneven burnt-stick lines and thumb-painted earth pigment, bare rough stone showing through. Flat ancient cave painting like Lascaux. Do not touch, redraw, erase or move Pepe or any ancestral motif. No new frog or hands; preserve both inherited five-digit hands. No letters, numbers, text, logos, captions, borders, frames, watermarks, real people or political symbols. Only add the tiny shelter and pebbles at that vacant area; everything else must stay exactly unchanged.
