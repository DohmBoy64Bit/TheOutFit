# Address Ledger

| Address | Type | Name | Evidence | Status | Notes |
|---|---|---|---|---|---|
| `0x8269A9B0` | Function / manual function range | `sub_8269A9B0` | Post-`IconMappings.map` smoke progressed to `fe.sga` and then watchdog state stayed around `lr=8269B000`, `ctr=8269B0A0`. Ghidra MCP decompilation showed caller `0x823F41C8` invoking `Function_8269A9B0(iVar2 + 4, 2)`. | Confirmed | Added `[functions."8269A9B0"] end = 0x8269BEE0` in `TheOutFit_Port/config/manual_functions.toml` so ReXGlue emits the full state-machine body. |
| `0x8269AB34` | Switch table / bctr dispatch | `sub_8269A9B0` state switch | Ghidra MCP disassembly identified a `bctr` switch at `0x8269AB34`, using index register `r10`, table `0x82031E60`, and base `0x8269AB38`. Ghidra MCP memory read of the halfword table produced 29 concrete target offsets. | Confirmed | Added a manual `[[switch_tables]]` entry with labels `0x8269AB38` through `0x8269BED8`. Local ignored SDK source was patched so manual switch labels are also used during block discovery, not only emission. This fixed the post-`fe.sga` wrong-label dispatch loop. |
| `0x8248C3E0` | Runtime crash site / manual function seed | `sub_8248C3E0_manual` | After the `0x8269AB34` switch fix, runtime failed with ReXGlue fatal: `Call to invalid or unregistered function at guest address 0x8248C3E0`. Ghidra MCP showed executable PPC at `0x8248C3E0` ending before adjacent function-like code at `0x8248C400`. | Confirmed | Added `[functions."8248C3E0"] size = 0x20` in `TheOutFit_Port/config/manual_functions.toml`; follow-up runtime no longer reported the invalid/unregistered function and reached GPU resolve / first-frame progress. |
| `0x821B8188` | GPU command-buffer function | `Function_821B8188` | During temporary first-chance exception diagnostics, host RVAs mapped to generated code for `sub_821B8188`; Ghidra MCP decompiled it as GPU command-buffer/register setup touching state from `0x826C8078` and emitting packet words. The process continued and rendered, so this was not classified as a fatal translated-code crash. | Confirmed | No seed or hook added. Temporary exception logging was removed after it proved noisy and non-fatal. |
| `0x821BB3B8` | GPU command-buffer function | `Function_821BB3B8` | Ghidra MCP decompiled it as another GPU memory/packet helper using `VdGlobalDevice`, `MmAllocatePhysicalMemoryEx`-style physical ranges, and texture/tile address math. It appeared in first-chance diagnostics but did not block rendering. | Confirmed | No seed or hook added. Kept as context for future GPU issues only. |
| `0x8269F910` | Branch source | Unknown | ReXGlue analysis error: `b 0x821E7A68 from 0x8269F910`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `8269f910: b 0x821e7a68`; no Ghidra function contains the source address. | Confirmed | Source sits in orphaned executable code near `0x8269F8E0..0x8269F917`, before `Function_8269F918`. The earlier stale read is superseded. |
| `0x821E7A68` | Jump target / manual function seed | `thunk_821E7A68_vtbl_10` | ReXGlue reported target not in any function. Ghidra MCP disassembles a six-instruction vtable thunk: `lis r11, -0x7d7a`; load `0x144c`; load vtable slot `0x10`; `mtspr CTR`; `bctr`. | Confirmed | Added `[functions."821E7A68"] size = 0x18` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |
| `0x82262790` | Branch source | Unknown | ReXGlue analysis error: `b 0x8226D6A0 from 0x82262790`; reproduced on `v0.8.0` and `0.8.1.4-dev.ge8ce24f`. Later Ghidra MCP context confirmed `82262790: b 0x8226d6a0`; no Ghidra function contains the source address. | Confirmed | Source follows a function-like block starting at `0x82262700` and precedes `Function_82262798`. The earlier stale read is superseded. |
| `0x8226D6A0` | Jump target / manual function seed | `sub_8226D6A0_manual` | ReXGlue reported target not in any function. Ghidra MCP disassembles executable PPC beginning `lwz r11, 0x1c(r3)`; gap evidence places it before `Function_8226D9F8`. | Confirmed | Added `[functions."8226D6A0"] end = 0x8226D9F8` in `TheOutFit_Port/config/manual_functions.toml`; this helped unblock codegen. |
| `0x826CA7D0` | Runtime special function | `longjmp` | Ghidra MCP disassembly shows jmp_buf restore behavior: normalizes zero return value to `1`, restores FPR14-FPR31, R13-R31, LR, CR, and SP, then returns through the restored LR. ReXGlue generated call sites now emit `ppc_longjmp(ctx.r3.u32, ctx.r4.s32)`. | Confirmed | Added as `longjmp_address = 0x826CA7D0` in `TheOutFit_Port/theoutfit_manifest.toml`. Function remains registered in generated output, but call sites are special-cased. |
| `0x826CAB30` | Runtime special function | `setjmp` | Ghidra MCP disassembly shows jmp_buf save behavior: stores FPR14-FPR31, R13-R31, LR, CR, and SP, clears a flag at `0x138`, and returns `0`. ReXGlue generated call sites now emit `ppc_setjmp(ctx.r3.u32)`. | Confirmed | Added as `setjmp_address = 0x826CAB30` in `TheOutFit_Port/theoutfit_manifest.toml`. Function remains registered in generated output, but call sites are special-cased. |
| `0x827D3DA8` | Runtime crash site / manual function seed | `sub_827D3DA8_manual` | First post-`game_data_root` runtime run failed with ReXGlue fatal: `Call to invalid or unregistered function at guest address 0x827D3DA8`. Ghidra MCP dry-run disassembly shows a six-instruction function-like branch stub ending with `b 0x8273e580`. Generated registration previously included `0x827D3D98` and `0x827D3DC0`, but not `0x827D3DA8`; after adding a `size = 0x18` manual seed, generated registration includes `0x827D3DA8`. | Confirmed | Added `[functions."827D3DA8"] size = 0x18` in `TheOutFit_Port/config/manual_functions.toml`; this fixed the invalid/unregistered function fatal. Current runtime reaches startup VFS warnings and stays alive until killed by the test harness. |

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
