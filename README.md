![The Outfit ReXGlue Port](imgs/readme_banner.png)

# The Outfit ReXGlue Port

This repository tracks an experimental native PC bring-up of the Xbox 360 version of *The Outfit* using [ReXGlue](https://github.com/rexglue/rexglue-sdk).

The goal is to make the game run as a native Windows application instead of through a full emulator. This is active reverse-engineering and runtime bring-up work, so the project is not ready for normal play yet.

**AI used for decomp research purposes and ghirdra MCP**

## Current Status

The port currently reaches the first rendered frame, menus, audio, and gameplay entry.

The main blocker is a later Direct3D 12 GPU hang during gameplay. The crash is not currently believed to be a missing game function; the evidence points toward ReXGlue's D3D12 render-target/resolve path.

Recent comparison with Xenia Canary is useful: current Canary D3D12 and Vulkan builds survive the same gameplay area that older Xenia and this port can crash in. That makes Canary a helpful research reference, but this project remains ReXGlue-only.

## What Is Included

- ReXGlue project files for *The Outfit*
- Manual function and switch-table configuration needed for the current build
- Focused local ReXGlue SDK patches stored as patch files
- Porting notes, address evidence, asset notes, and regression history
- Helper scripts for read-only PowerPC/XEX investigation
- A Visual Studio debug wrapper that launches the verified CMake build

## What Is Not Included

This repository does not include the game.

Do not commit or upload:

- ISO files
- XEX files
- extracted game assets
- copyrighted game data
- generated ReXGlue output
- logs, screenshots, binaries, or local build output

The expected local game data path is:

```text
D:\360RexGlue\TheOutFit\assets\game_files
```

The canonical local ISO path used during development is:

```text
D:\360RexGlue\TheOutFit\theoutfit.iso
```

Both are ignored and must remain local.

## ISO And Game Asset Extraction

You need your own legally owned copy of the Xbox 360 game. Place the local ISO at the canonical path used by this workspace:

```text
D:\360RexGlue\TheOutFit\theoutfit.iso
```

Extract the ISO into the ignored game data folder:

```text
D:\360RexGlue\TheOutFit\assets\game_files
```

This workspace has used `extract-xiso` for the local extraction. The exact command can vary by tool build, but the important result is that the extracted entrypoint exists here:

```text
D:\360RexGlue\TheOutFit\assets\game_files\default.xex
```

Launch the port with that extracted folder as the game data root:

```cmd
--game_data_root=D:\360RexGlue\TheOutFit\assets\game_files
```

Keep the ISO and extracted files out of Git. `docs/asset_ledger.md` records local hashes and evidence, but not game content.

## Required Game Version

This port expects a legally owned Xbox 360 copy of *The Outfit* extracted locally.

Known local ISO evidence used during development:

- File: `theoutfit.iso`
- SHA-256: `9112A8E01719FC52749D0A735CD0CF44CE11C9F575714F0467B4EE30F7F5353A`
- Extracted entrypoint: `assets/game_files/default.xex`
- `default.xex` SHA-256: `1BD7C232574681D51865C40383581F4157592991998BC6CE085E24CE38325654`

The project does not host, link to, or endorse downloads of copyrighted game files. 
You can find 'info' on the proper 'legally' obtained backup copy [here](https://vimm.net/vault/78710)

## Project Layout

| Path | Purpose |
|---|---|
| `TheOutFit_Port/` | Main ReXGlue port project, manifest, config, source, and Visual Studio wrapper. |
| `TheOutFit_Port/config/manual_functions.toml` | Current manual function seeds and switch-table entries. |
| `docs/` | Human-readable notes, ledgers, build history, and regression evidence. |
| `docs/rexglue_patches/` | Local ReXGlue SDK patches used or investigated by this port. |
| `scripts/` | Read-only helper scripts for research and verification. |
| `imgs/` | Public README images. |

## Build Requirements

The verified Windows setup uses:

- Visual Studio 2022 Community or Build Tools
- LLVM / Clang
- CMake
- Ninja
- Python
- Git
- ReXGlue SDK checked out locally under `tools/rexglue-sdk`

The exact commands and environment notes live in `docs/toolchain.md`.

## ReXGlue SDK Setup

Clone ReXGlue into the ignored `tools/` folder:

```cmd
cd /d D:\360RexGlue\TheOutFit
git clone --recursive https://github.com/rexglue/rexglue-sdk.git tools\rexglue-sdk
```

Apply the required local SDK patches from the ReXGlue checkout:

```cmd
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
```

Build and install the SDK:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cmake --preset win-amd64
cmake --build --preset win-amd64-relwithdebinfo --target install
```

Optional diagnostic patches are documented in `docs/rexglue_patches/README.md`. They are not required by default.

## Generate ReXGlue Code

Before building the port, the extracted `default.xex` must exist here:

```text
D:\360RexGlue\TheOutFit\assets\game_files\default.xex
```

The manifest already points at that file:

```text
TheOutFit_Port\theoutfit_manifest.toml
```

Run codegen from the port directory:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
..\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe codegen .\theoutfit_manifest.toml
```

This creates reproducible generated code under:

```text
TheOutFit_Port\generated\default
```

That folder is ignored and should not be committed. Re-run codegen after changing the manifest, manual function config, switch-table config, or after replacing the extracted `default.xex`.

## Build The Port

From the port directory:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
cmake --preset win-amd64-relwithdebinfo
cmake --build --preset win-amd64-relwithdebinfo
```

The executable is generated at:

```text
TheOutFit_Port\out\build\win-amd64-relwithdebinfo\theoutfit.exe
```

Build output is ignored.

## Run A Smoke Test

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe
```

The executable auto-detects extracted game files in `game_files` beside the executable, `assets\game_files` beside the executable, or the same folders in nearby parent directories. You can still override the detected path explicitly with `--game_data_root=<path>`.

For debugging, use trace logging:

```cmd
theoutfit.exe --log_level=trace --log_noisy --log_flush_interval=1 --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-smoke.log
```

Logs are ignored and should not be uploaded.

## Visual Studio Debugging

Open:

```text
TheOutFit_Port\TheOutFit_Debug.sln
```

This solution is a small wrapper around the verified CMake/Ninja/Clang build. It launches the RelWithDebInfo executable and uses the same automatic game-data folder detection as direct runs.

## Current Technical Notes

- ReXGlue version used locally: `0.8.1.4-dev.ge8ce24f`.
- Required local SDK patches: `0001` and `0002`.
- Diagnostic SDK patches `0003` through `0006` are tracked but not required by default.
- Generated ReXGlue code is reproducible and ignored at `TheOutFit_Port/generated/default`.
- Latest active investigation: D3D12 host-render-target/direct-resolve/dump behavior after repeated resolve/coherency traffic.
- Canary-mirrored ReXGlue cvar tests did not fix the TDR.

For details, see:

- `docs/regression_log.md`
- `docs/toolchain.md`
- `docs/address_ledger.md`
- `docs/asset_ledger.md`
- `docs/rexglue_patches/README.md`

## Research Rules

This project uses ReXGlue as the active porting path. Xenia Canary is used only as a research reference for comparing behavior.

For guest-code investigation, use Ghidra MCP first when available. Manual Ghidra lookup is fallback only.

## Credits

- Original game: *The Outfit* by Relic Entertainment, published by THQ.
- Recompilation/runtime framework: [ReXGlue](https://github.com/rexglue/rexglue-sdk).
- Static analysis bridge: [bethington/ghidra-mcp](https://github.com/bethington/ghidra-mcp).
- Comparative emulator research: [Xenia Canary](https://github.com/xenia-canary/xenia-canary).
- Community recomp references used for layout and documentation research only: TiP-Recomp, reNut, redahm, Re-Cherry, and NaughtyBear_ReStuff.

This repository does not include or distribute game content.
