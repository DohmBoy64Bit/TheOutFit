# Agent Instructions

## Project Scope
- This project uses ReXGlue as the selected end-to-end Xbox 360 static recompilation/runtime pipeline.
- Do not combine ReXGlue with XenonRecomp as sequential workflow stages.
- Do not introduce XenonAnalyse/XenonRecomp unless the user explicitly switches workflows.

## Evidence Rules
- Verify ReXGlue commands, config fields, hook macros, generated paths, and runtime APIs from local ReXGlue source/docs or tool output before recommending them.
- Use `bethington/ghidra-mcp` first for function, disassembly, decompiler, xref, and data-reference evidence.
- Use manual Ghidra lookup only as fallback when MCP is unavailable or insufficient.
- Label whether evidence came from local files, ReXGlue output, Ghidra MCP, helper scripts, or user-provided artifacts.

## Local Helpers
- Use `scripts/xref_ppc_in_xex.py` for read-only PPC xref/disassembly/heuristic `bctr` scans when useful.
- Treat `scripts/translate_switch_tables.py` as reference-only, not current ReXGlue source of truth.

## Asset Boundaries
- Canonical source ISO: `D:\360RexGlue\TheOutFit\theoutfit.iso`.
- Do not commit or distribute copyrighted game binaries, decrypted assets, keys, or proprietary content.
- Keep source, configs, docs, scripts, and reproducible metadata separate from proprietary binaries/assets.

## Build and Test
- List only verified commands here. Do not include aspirational commands.
- Current shell can run Git, CMake, and Python. `clang-cl.exe` exists at `C:\Program Files\LLVM\bin\clang-cl.exe` but is not currently on PATH.

## Documentation Discipline
- Keep `docs/asset_ledger.md`, `docs/address_ledger.md`, and `docs/regression_log.md` current during porting work.
- Document hooks with guest address, original PPC instruction window, registers touched, memory ranges touched, continuation behavior, and verification method.
- Do not call a change correct merely because a crash moved or disappeared.
