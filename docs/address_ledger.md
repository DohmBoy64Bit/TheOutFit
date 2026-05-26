# Address Ledger

| Address | Type | Name | Evidence | Status | Notes |
|---|---|---|---|---|---|
| `0x8269F910` | Branch source | Unknown | ReXGlue analysis error: `b 0x821E7A68 from 0x8269F910`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `8269f910: b 0x821e7a68`; no Ghidra function contains the source address. | Confirmed | Source sits in orphaned executable code near `0x8269F8E0..0x8269F917`, before `Function_8269F918`. The earlier stale read is superseded. |
| `0x821E7A68` | Jump target / manual function seed | `thunk_821E7A68_vtbl_10` | ReXGlue reported target not in any function. Ghidra MCP disassembles a six-instruction vtable thunk: `lis r11, -0x7d7a`; load `0x144c`; load vtable slot `0x10`; `mtspr CTR`; `bctr`. | Confirmed | Added `[functions."821E7A68"] size = 0x18` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |
| `0x82262790` | Branch source | Unknown | ReXGlue analysis error: `b 0x8226D6A0 from 0x82262790`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `82262790: b 0x8226d6a0`; no Ghidra function contains the source address. | Confirmed | Source follows a function-like block starting at `0x82262700` and precedes `Function_82262798`. The earlier stale read is superseded. |
| `0x8226D6A0` | Jump target / manual function seed | `sub_8226D6A0_manual` | ReXGlue reported target not in any function. Ghidra MCP disassembles executable PPC beginning `lwz r11, 0x1c(r3)`; gap evidence places it before `Function_8226D9F8`. | Confirmed | Added `[functions."8226D6A0"] end = 0x8226D9F8` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |
| `0x826CA7D0` | Runtime special function | `longjmp` | Ghidra MCP disassembly shows jmp_buf restore behavior: normalizes zero return value to `1`, restores FPR14-FPR31, R13-R31, LR, CR, and SP, then returns through the restored LR. ReXGlue generated call sites now emit `ppc_longjmp(ctx.r3.u32, ctx.r4.s32)`. | Confirmed | Added as `longjmp_address = 0x826CA7D0` in `TheOutFit_Port/theoutfit_manifest.toml`. Function remains registered in generated output, but call sites are special-cased. |
| `0x826CAB30` | Runtime special function | `setjmp` | Ghidra MCP disassembly shows jmp_buf save behavior: stores FPR14-FPR31, R13-R31, LR, CR, and SP, clears a flag at `0x138`, and returns `0`. ReXGlue generated call sites now emit `ppc_setjmp(ctx.r3.u32)`. | Confirmed | Added as `setjmp_address = 0x826CAB30` in `TheOutFit_Port/theoutfit_manifest.toml`. Function remains registered in generated output, but call sites are special-cased. |
| `0x827D3DA8` | Runtime crash site / missing function registration | Unknown | First post-`game_data_root` runtime run fails with ReXGlue fatal: `Call to invalid or unregistered function at guest address 0x827D3DA8`. Ghidra MCP dry-run disassembly shows a function-like block: `lis r11, -0x7d7a`; `subi r4, r11, 0x365c`; `lis r11, -0x7d7a`; `subi r3, r11, 0x3638`; `b 0x8273e580`. Generated registration includes `0x827D3D98` and `0x827D3DC0`, but not `0x827D3DA8`. Runtime still fails here after configuring `setjmp_address`/`longjmp_address` and rebuilding. | Broken | Next likely fix is a missing function boundary/registration inside generated translated code. Verify whether `[functions."827D3DA8"] size = 0x18` is the correct ReXGlue config fix before adding it. |

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
