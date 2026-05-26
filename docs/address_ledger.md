# Address Ledger

| Address | Type | Name | Evidence | Status | Notes |
|---|---|---|---|---|---|
| `0x8269F910` | Reported branch source | Unknown | ReXGlue analysis error: `b 0x821E7A68 from 0x8269F910`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Ghidra MCP disassembles this address as `beq cr6, 0x8269f920`, not a branch to `0x821E7A68`. | Broken | Candidate ReXGlue branch/source labeling mismatch. Needs MCP function-boundary/xref follow-up before any manifest or hook change. |
| `0x821E7A68` | Jump target | Unknown | ReXGlue analysis error target; Ghidra MCP disassembles valid executable PPC beginning at `lis r11, -0x7df7`. | Unknown | ReXGlue reported target not in any function. Needs function-boundary confirmation in Ghidra MCP. |
| `0x82262790` | Reported branch source | Unknown | ReXGlue analysis error: `b 0x8226D6A0 from 0x82262790`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Ghidra MCP disassembles this address as `fmr f3, f30`, not a branch. | Broken | Candidate ReXGlue branch/source labeling mismatch. Needs MCP function-boundary/xref follow-up before any manifest or hook change. |
| `0x8226D6A0` | Jump target | Unknown | ReXGlue analysis error target; Ghidra MCP disassembles valid executable PPC beginning at `beq 0x8226d8a4`. | Unknown | ReXGlue reported target not in any function. Needs function-boundary confirmation in Ghidra MCP. |

## Status Values
- Confirmed
- Probable
- Unknown
- Deprecated
- Broken
- Replaced by hook

## Type Examples
- Function
- Hook
- Crash site
- Jump target
- Data object
- Vtable
- String
- Import/stub
- MMIO access
- Asset reference
