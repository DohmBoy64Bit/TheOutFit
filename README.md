# TheOutFit ReXGlue Port

This repository tracks the source, configuration, documentation, and reproducible notes for a ReXGlue-based Xbox 360 recompilation/runtime bring-up of *The Outfit*.

The project is currently ReXGlue-only. It does not use XenonRecomp or XenonAnalyse as workflow stages.

## Current Status

- ReXGlue SDK version used locally: `0.8.1.4-dev.ge8ce24f`.
- Canonical local source artifact: `D:\360RexGlue\TheOutFit\theoutfit.iso`.
- Canonical extracted game root: `D:\360RexGlue\TheOutFit\assets\game_files`.
- Current runtime milestone: first rendered frame reached in RelWithDebInfo with no fatal/error/critical lines in the final smoke log.
- Generated ReXGlue output is reproducible and ignored at `TheOutFit_Port/generated/default`.
- Local ReXGlue SDK checkout/build output is ignored under `tools/`.

See `docs/regression_log.md` for the exact evidence chain.

## Repository Contents

| Path | Purpose |
|---|---|
| `TheOutFit_Port/` | ReXGlue project manifest, CMake project, app customization, and Visual Studio debug wrapper. |
| `TheOutFit_Port/config/manual_functions.toml` | Manual function seeds and switch-table config needed for current codegen/runtime progress. |
| `TheOutFit_Port/src/theoutfit_app.h` | Project-side lifecycle and register-only watchdog diagnostics. |
| `docs/` | Porting ledgers, verified toolchain commands, regression history, and local SDK patches. |
| `docs/rexglue_patches/` | Tracked patch files for the ignored local ReXGlue SDK checkout. |
| `scripts/xref_ppc_in_xex.py` | Read-only helper for PPC/XEX xref and heuristic scans. |
| `scripts/translate_switch_tables.py` | Reference-only helper; not source of truth for ReXGlue behavior. |
| `AGENTS.md` | Required instructions for future AI agent work in this repository. |
| `SystemPrompt.md` | Project-specific system prompt/handoff guidance. |

## Asset Policy

This repository must not contain copyrighted game binaries, decrypted assets, keys, generated proprietary screenshots, logs with proprietary payloads, or the source ISO.

Ignored local inputs include:

- `theoutfit.iso`
- `assets/game_files/`
- `*.xex`, `*.iso`, `*.dvd`, `*.xbe`, `*.wad`
- `TheOutFit_Port/generated/default/`
- `TheOutFit_Port/out/`
- `docs/logs/*.png`
- `tools/`

Document local assets in `docs/asset_ledger.md` before using them as evidence. Do not commit the assets themselves.

## Required Local Setup

The verified Windows setup uses:

- Git
- CMake
- Ninja
- Python
- Visual Studio 2022 Community / Build Tools
- LLVM with `clang-cl.exe`
- ReXGlue SDK checkout at `tools/rexglue-sdk`
- Ghidra MCP via `bethington/ghidra-mcp` for guest-address research

See `docs/toolchain.md` for exact verified versions and command output.

## ReXGlue SDK Setup

Clone/build the ReXGlue SDK locally under ignored `tools/`:

```cmd
cd /d D:\360RexGlue\TheOutFit
git clone --recursive https://github.com/rexglue/rexglue-sdk.git tools\rexglue-sdk
```

Apply the tracked local SDK patches from the SDK checkout root:

```cmd
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
```

Build and install ReXGlue:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk
cmake --preset win-amd64
cmake --build --preset win-amd64-relwithdebinfo --target install
```

The current local workflow requires the two tracked patches:

- `0001-use-manual-switch-tables-during-block-discovery.patch`: makes manual `[[switch_tables]]` labels participate in block discovery.
- `0002-tolerate-modifier-only-physical-protection.patch`: treats modifier-only physical allocation protection such as `0x400` / `X_PAGE_WRITECOMBINE` as read/write physical memory.

## Game Data Setup

The project expects extracted game files at:

```text
D:\360RexGlue\TheOutFit\assets\game_files
```

The ReXGlue manifest expects `default.xex` in that tree. The local source ISO and extracted game files are ignored and must remain local.

Current documented local inputs:

- `theoutfit.iso`
- `assets/game_files/default.xex`
- `assets/game_files/Common/WW2/Locale/English/IconMappings.map`
- `assets/game_files/ingame_ui.XZP`

See `docs/asset_ledger.md` for hashes and status.

## Code Generation

Run codegen from the ReXGlue project directory:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
..\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe --log-level debug --log-file ..\docs\logs\codegen-manual-functions-debug.log codegen .\theoutfit_manifest.toml
```

Generated output goes to:

```text
TheOutFit_Port\generated\default
```

That directory is intentionally ignored.

## Build

Use the verified RelWithDebInfo preset:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
cmake --preset win-amd64-relwithdebinfo
cmake --build --preset win-amd64-relwithdebinfo
```

The executable is produced under ignored build output:

```text
TheOutFit_Port\out\build\win-amd64-relwithdebinfo\theoutfit.exe
```

## Runtime Smoke Test

Verified first-frame smoke command:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_noisy --log_flush_interval=1 --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-first-frame-no-errors.log
```

Final verified result:

- Process stayed alive until killed by the smoke-test harness.
- Visible first rendered frame was captured locally, then removed from the worktree.
- `runtime-first-frame-no-errors.log` had no fatal/error/critical lines.
- Repeated GPU `Resolve` progress was present.

Logs remain ignored.

## Visual Studio Debugging

`TheOutFit_Port/TheOutFit_Debug.sln` is a tracked Visual Studio Makefile wrapper. It delegates build/rebuild/clean to the verified CMake/Ninja/Clang RelWithDebInfo path and debugs:

```text
TheOutFit_Port\out\build\win-amd64-relwithdebinfo\theoutfit.exe
```

The debug wrapper passes:

```cmd
--game_data_root=D:\360RexGlue\TheOutFit\assets\game_files
```

Do not replace this with a normal MSVC-generated project unless the generated ReXGlue C++ and SDK are verified to build under that path.

## Documentation Discipline

Keep these files updated as part of every meaningful porting change:

- `README.md`: current project status, setup, build/run workflow, and maintenance rules.
- `docs/toolchain.md`: verified commands, tools, SDK setup, and local SDK patch requirements.
- `docs/regression_log.md`: every hook, runtime stub, config edit, generated-project patch, build milestone, and crash movement.
- `docs/address_ledger.md`: concrete guest addresses confirmed from ReXGlue logs, debugger evidence, generated frame names, helper scripts, or Ghidra MCP.
- `docs/asset_ledger.md`: local asset paths, hashes, and proprietary-boundary notes.
- `AGENTS.md`: active instructions for future agents.

Do not call a change correct merely because a crash moved or disappeared. Record the evidence and classification.

## Guest Analysis Rules

- Use `bethington/ghidra-mcp` first for function, disassembly, decompiler, xref, and data-reference evidence.
- Use manual Ghidra lookup only as fallback.
- Use `scripts/xref_ppc_in_xex.py` as a read-only helper when useful.
- Treat `scripts/translate_switch_tables.py` as reference-only.
- Label whether evidence came from local files, ReXGlue output, Ghidra MCP, helper scripts, or user-provided artifacts.

## Current Tracked ReXGlue Manual Coverage

Current `manual_functions.toml` includes coverage for:

- `0x821E7A68`
- `0x8226D6A0`
- `0x827D3DA8`
- `0x8248C3E0`
- `0x8269A9B0..0x8269BEE0`
- switch table at `0x8269AB34`

See `docs/address_ledger.md` for evidence and notes.

## Commit Hygiene

Commit candidates:

- source
- configs
- docs
- scripts
- reproducible metadata
- tracked patch files

Never commit:

- ISO files
- XEX files
- extracted game assets
- generated ReXGlue output
- build output
- `.pdb`, `.exe`, `.dll`
- Visual Studio local state
- raw logs
- screenshots of proprietary rendered content

## Open Items

- Keep first-frame runtime status reproducible after SDK or ReXGlue updates.
- Decide later whether generated ReXGlue output should remain ignored or become part of a reproducible release workflow.
- Upstream or otherwise formalize the two local ReXGlue SDK patches if they remain generally useful.
