# Toolchain Audit

## Verified On 2026-05-26

| Tool | Result | Notes |
|---|---|---|
| Git | `git version 2.52.0.windows.1` | Available on PATH. |
| CMake | `cmake version 4.2.1` | Available on PATH. |
| Python | `Python 3.13.7` | Available via `python` and `py`. Project scripts may require dependency setup before use. |
| LLVM clang-cl | `clang version 22.1.5`, target `x86_64-pc-windows-msvc` | Found at `C:\Program Files\LLVM\bin\clang-cl.exe`; not currently available through `where clang-cl`. |
| Ghidra MCP | 196 tools loaded | `bethington/ghidra-mcp` bridge is reachable with function, listing, xref, analysis, datatype, debugger, and program tool groups loaded. |
| Ninja | `1.13.2` | Available on PATH through WinGet links. |
| Visual Studio 2022 | `C:\Program Files\Microsoft Visual Studio\2022\Community` | `vcvars64.bat` is required so Clang can find MSVC/Windows SDK libraries. |
| ReXGlue SDK | `v0.8.1.4-dev.ge8ce24f` | Cloned recursively to `D:\360RexGlue\TheOutFit\tools\rexglue-sdk`, configured with `win-amd64`, and installed to `tools\rexglue-sdk\out\install\win-amd64`. |

## Verified ReXGlue Commands

Run these from a shell where Visual Studio x64 environment has been initialized and LLVM is on `PATH`:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk
cmake --preset win-amd64
cmake --build --preset win-amd64-release --target install
```

Verified CLI:

```cmd
D:\360RexGlue\TheOutFit\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe --help
```

The installed CLI reports subcommands:

- `codegen`
- `init`
- `recompile-tests`

Verified project initialization command:

```cmd
D:\360RexGlue\TheOutFit\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe init --project-name TheOutFit --xex-path .\assets\game_files\default.xex --game-root .\assets\game_files --project-root .\TheOutFit_Port
```

Generated project:

- `TheOutFit_Port\theoutfit_manifest.toml`
- `TheOutFit_Port\CMakeLists.txt`
- `TheOutFit_Port\CMakePresets.json`
- `TheOutFit_Port\generated\rexglue.cmake`
- `TheOutFit_Port\src\main.cpp`
- `TheOutFit_Port\src\theoutfit_app.h`

Verified generated project configure:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
cmake --list-presets
cmake --preset win-amd64-debug
```

Result: CMake found ReXGlue SDK `0.8.1.4-dev.ge8ce24f` at `D:\360RexGlue\TheOutFit\tools\rexglue-sdk\out\install\win-amd64\lib\cmake\rexglue` and generated build files under ignored `TheOutFit_Port\out\build\win-amd64-debug`.

Verified first codegen reconnaissance command:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
..\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe --log-level debug --log-file ..\docs\logs\codegen-first-debug.log codegen .\theoutfit_manifest.toml
```

Result: ReXGlue reached analysis sealing, then failed with `UnresolvedCall (2)` for `0x821E7A68 from 0x8269F910` and `0x8226D6A0 from 0x82262790`. No `TheOutFit_Port\generated\default` directory was produced. Later Ghidra MCP context corroborated both source addresses as direct branches and both targets as executable code, so this was missing function coverage for orphaned executable code rather than a confirmed branch/source labeling bug.

Verified stable `v0.8.0` A/B build:

```cmd
git clone --recursive --branch v0.8.0 https://github.com/rexglue/rexglue-sdk.git D:\360RexGlue\TheOutFit\tools\rexglue-sdk-v0.8.0
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk-v0.8.0
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cmake --preset win-amd64
cmake --build --preset win-amd64-release --target install
```

The `v0.8.0` binary reports `0.8.0` from tag commit `2bdb97f`. Its codegen result was identical to the dev build:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
..\tools\rexglue-sdk-v0.8.0\out\install\win-amd64\bin\rexglue.exe --log-level debug --log-file ..\docs\logs\codegen-v0.8.0-debug.log codegen .\theoutfit_manifest.toml
```

Result: same `UnresolvedCall (2)` at `0x821E7A68 from 0x8269F910` and `0x8226D6A0 from 0x82262790`; no generated output. Therefore switching from `0.8.1.4-dev.ge8ce24f` to the stable `v0.8.0` tag does not resolve the first codegen blocker.

Verified manual function seed codegen:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
..\tools\rexglue-sdk\out\install\win-amd64\bin\rexglue.exe --log-level debug --log-file ..\docs\logs\codegen-manual-functions-debug.log codegen .\theoutfit_manifest.toml
```

Result: ReXGlue loaded `config/manual_functions.toml`, added or updated 2 function entries, and codegen succeeded. It produced `TheOutFit_Port\generated\default` with 61 files totaling about 122.5 MB. That directory is ignored as reproducible generated output.

Verified release build after codegen:

```cmd
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
set PATH=C:\Program Files\LLVM\bin;%PATH%
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
cmake --preset win-amd64-release
cmake --build --preset win-amd64-release
```

Result: release configure/build succeeded and linked `theoutfit.exe` under ignored `TheOutFit_Port\out\build\win-amd64-release`.

Verified Visual Studio debug project:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port
"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\amd64\MSBuild.exe" TheOutFit_Debug.sln /p:Configuration=RelWithDebInfo /p:Platform=x64 /m
```

Result: `TheOutFit_Debug.sln` builds successfully through a Visual Studio Makefile project. The project delegates build/rebuild/clean to the verified `win-amd64-relwithdebinfo` Ninja/Clang preset and debugs `out\build\win-amd64-relwithdebinfo\theoutfit.exe`.

The current Visual Studio debug wrapper passes no game-data argument. `TheoutfitApp::OnConfigurePaths` auto-detects the extracted game-data folder by looking for `default.xex` in `game_files` or `assets\game_files` beside the executable and nearby parent directories.

Direct runtime smoke command using auto-detected game data:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe
```

The explicit override is still supported:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files
```

Result: the previous `--game_data_root was not provided` blocker is fixed. Runtime setup proceeds through game directory mount, XEX image load, and module launch, then fails on invalid/unregistered guest function `0x827D3DA8`.

After adding `[functions."827D3DA8"] size = 0x18` to `config/manual_functions.toml`, regenerating, and rebuilding RelWithDebInfo, the invalid/unregistered function fatal is fixed. Runtime remains alive until killed by the test harness. The next observed warnings are VFS misses for several title paths, including `D:\COMMON\ENGINE\DATA`, `D:\XENON\ENGINE\DATA`, `D:\COMMON\ENGINE\MOVIES`, `D:\LocaleData:\`, and `D:\common\ww2\locale\English\IconMappings.map`.

Verified first-frame trace invocation:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-first-frame-trace.log --gpu_debug_markers --dump_shaders=D:\360RexGlue\TheOutFit\docs\logs\shader-dumps-first-frame
```

Result: the process stayed alive until killed by the 120s smoke-test timeout. No first-frame, shader dump, swap, or present evidence was observed. A noisy follow-up showed `IconMappings.map` exists inside `Common\WW2\Locale\English\XModLoc.sga`; extracting that canonical payload locally to ignored `assets\game_files\Common\WW2\Locale\English\IconMappings.map` removed the direct loose-file open failure, but the runtime still did not reach first frame.

Verified D3D12 TDR investigation:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_noisy --log_flush_interval=1 --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-until-crash.log
```

Result: local interaction reached first frame, menus, audio, and gameplay entry. A later run failed with `D3D12 device removed: HRESULT 0x887A0006 - DEVICE_HUNG (TDR - GPU command took too long)` and exit `0xC0000409`. Last log evidence before the TDR was repeated GPU resolve/coherency traffic, not an invalid/unregistered guest function.

Diagnostic D3D12 debug/DRED invocation:

```cmd
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_noisy --log_flush_interval=1 --d3d12_debug --gpu_debug_markers --trace_gpu_prefix=D:\360RexGlue\TheOutFit\docs\logs\gpu-traces\d3d12-tdr --dump_shaders=D:\360RexGlue\TheOutFit\docs\logs\shader-dumps-tdr --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-d3d12-dred.log
```

Result: DRED was enabled and shaders were dumped, but this changed the run to early exit `0xC000008F` before useful DRED breadcrumbs were emitted.

Current candidate D3D12 mitigation:

```cmd
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_noisy --log_flush_interval=1 --d3d12_submit_on_primary_buffer_end=false --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-bisect-submit-on-primary-buffer-end-false.log
```

Result: the rotated log set initially contained no fatal/error/critical/device-hung lines and ended with clean window shutdown messages, but later passive comparison runs reproduced `DEVICE_HUNG` with this flag. `--direct_host_resolve=false` was also tested and did not prevent `DEVICE_HUNG`.

## Local SDK Notes

- The first configure attempt failed outside the Visual Studio developer environment because `oldnames.lib` and `msvcrtd.lib` were not visible to the linker.
- The Windows checkout materialized `libmspack` symlink placeholders as text files because `core.symlinks=false`; local ignored SDK files under `thirdparty/libmspack/cabextract/mspack` were copied from their referenced targets before the install build succeeded.
- The current first-frame workflow requires only the minimal tracked local SDK patches in `docs\rexglue_patches\`. Apply them from `tools\rexglue-sdk` before rebuilding/installing ReXGlue:

```cmd
cd /d D:\360RexGlue\TheOutFit\tools\rexglue-sdk
git apply ..\..\docs\rexglue_patches\0001-use-manual-switch-tables-during-block-discovery.patch
git apply ..\..\docs\rexglue_patches\0002-tolerate-modifier-only-physical-protection.patch
```

- Patch `0001` makes manual switch-table labels participate in block discovery for the `0x8269AB34` bctr state switch. Patch `0002` treats modifier-only physical allocation protection such as `0x400` (`X_PAGE_WRITECOMBINE`) as read/write, removing the final `MmAllocatePhysicalMemoryEx: bad protection bits` errors seen before first frame.
- Patch `0003` is no longer classified as required. It adds a conservative D3D12 primary-buffer submission guard for pending UAV/EDRAM work, but it is not independently sufficient to fix the current TDR and should be applied only for comparison or diagnostic experiments.

Optional D3D12 diagnostic/experimental patches:

```cmd
git apply ..\..\docs\rexglue_patches\0003-defer-d3d12-primary-submission-with-pending-uav-work.patch
git apply ..\..\docs\rexglue_patches\0004-diagnose-d3d12-shared-memory-coherency.patch
git apply ..\..\docs\rexglue_patches\0005-diagnose-d3d12-resolve-coherency-loop.patch
git apply ..\..\docs\rexglue_patches\0006-diagnose-d3d12-host-render-target-extent-and-resolve.patch
```

Current D3D12 comparison command shape after the `0x827558F0` thunk-seed pass:

```cmd
cd /d D:\360RexGlue\TheOutFit\TheOutFit_Port\out\build\win-amd64-relwithdebinfo
theoutfit.exe --game_data_root=D:\360RexGlue\TheOutFit\assets\game_files --log_level=trace --log_noisy --log_flush_interval=1 --d3d12_tiled_shared_memory=false --d3d12_submit_on_primary_buffer_end=false --log_file=D:\360RexGlue\TheOutFit\docs\logs\runtime-after-seed-827558F0-tiled-false-submit-false.log
```

Result: an earlier 120s passive smoke stayed alive until the harness killed it and showed no matched fatal/error/critical/device-hung lines, but later comparison runs reproduced `DEVICE_HUNG`. Do not treat this flag pair as a fix.

## Open Items
- Add the ReXGlue install `bin` directory to command sessions when invoking `rexglue` directly, or call `rexglue.exe` by full path.
- Keep `tools/` ignored; do not commit the third-party SDK checkout, build output, install tree, or local tool binaries.
- Debug build currently fails at link time because debug objects use `_ITERATOR_DEBUG_LEVEL=2` while installed SDK libraries such as `spdlog.lib` were built with `_ITERATOR_DEBUG_LEVEL=0`; use the verified release preset unless a debug SDK build is prepared.
- Do not use a normal CMake Visual Studio/MSVC generated project for ReXGlue output. The generated C++ uses Clang/GNU builtins and attributes, so the tracked Visual Studio solution is a Makefile project that invokes the known-good Clang/Ninja build instead.
