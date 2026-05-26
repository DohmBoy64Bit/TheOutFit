# Toolchain Audit

## Verified On 2026-05-26

| Tool | Result | Notes |
|---|---|---|
| Git | `git version 2.52.0.windows.1` | Available on PATH. |
| CMake | `cmake version 4.2.1` | Available on PATH. |
| Python | `Python 3.13.7` | Available via `python` and `py`. Project scripts may require dependency setup before use. |
| LLVM clang-cl | `clang version 22.1.5`, target `x86_64-pc-windows-msvc` | Found at `C:\Program Files\LLVM\bin\clang-cl.exe`; not currently available through `where clang-cl`. |
| Ghidra MCP | 196 tools loaded | `bethington/ghidra-mcp` bridge is reachable with function, listing, xref, analysis, datatype, debugger, and program tool groups loaded. |

## Open Items
- Confirm Visual Studio Build Tools or Windows SDK environment before native build work.
- Locate or install ReXGlue SDK/source and verify all commands from local docs/source or help output before use.
