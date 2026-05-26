# Address Ledger

| Address | Type | Name | Evidence | Status | Notes |
|---|---|---|---|---|---|
| `0x8269F910` | Branch source | Unknown | ReXGlue analysis error: `b 0x821E7A68 from 0x8269F910`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `8269f910: b 0x821e7a68`; no Ghidra function contains the source address. | Confirmed | Source sits in orphaned executable code near `0x8269F8E0..0x8269F917`, before `Function_8269F918`. The earlier stale read is superseded. |
| `0x821E7A68` | Jump target / manual function seed | `thunk_821E7A68_vtbl_10` | ReXGlue reported target not in any function. Ghidra MCP disassembles a six-instruction vtable thunk: `lis r11, -0x7d7a`; load `0x144c`; load vtable slot `0x10`; `mtspr CTR`; `bctr`. | Confirmed | Added `[functions."821E7A68"] size = 0x18` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |
| `0x82262790` | Branch source | Unknown | ReXGlue analysis error: `b 0x8226D6A0 from 0x82262790`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `82262790: b 0x8226d6a0`; no Ghidra function contains the source address. | Confirmed | Source follows a function-like block starting at `0x82262700` and precedes `Function_82262798`. The earlier stale read is superseded. |
| `0x8226D6A0` | Jump target / manual function seed | `sub_8226D6A0_manual` | ReXGlue reported target not in any function. Ghidra MCP disassembles executable PPC beginning `lwz r11, 0x1c(r3)`; gap evidence places it before `Function_8226D9F8`. | Confirmed | Added `[functions."8226D6A0"] end = 0x8226D9F8` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |

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
