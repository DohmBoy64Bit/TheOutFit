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

## Local SDK Notes

- The first configure attempt failed outside the Visual Studio developer environment because `oldnames.lib` and `msvcrtd.lib` were not visible to the linker.
- The Windows checkout materialized `libmspack` symlink placeholders as text files because `core.symlinks=false`; local ignored SDK files under `thirdparty/libmspack/cabextract/mspack` were copied from their referenced targets before the install build succeeded.

## Open Items
- Add the ReXGlue install `bin` directory to command sessions when invoking `rexglue` directly, or call `rexglue.exe` by full path.
- Keep `tools/` ignored; do not commit the third-party SDK checkout, build output, install tree, or local tool binaries.
