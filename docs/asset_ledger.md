# Asset Ledger

| Artifact | Path | SHA-256 | Size | Status | Notes |
|---|---|---|---:|---|---|
| Canonical source ISO | `D:\360RexGlue\TheOutFit\theoutfit.iso` | `9112A8E01719FC52749D0A735CD0CF44CE11C9F575714F0467B4EE30F7F5353A` | 7,834,892,288 bytes | Confirmed | User confirmed this lawful ISO is the source artifact for the project. Do not commit it. |
| Extracted entrypoint XEX | `D:\360RexGlue\TheOutFit\assets\game_files\default.xex` | `1BD7C232574681D51865C40383581F4157592991998BC6CE085E24CE38325654` | 9,056,256 bytes | Confirmed | Extracted from the canonical ISO with `extract-xiso`; used as ReXGlue `entrypoint.file_path`. Do not commit it. |

## Policy
- Keep an untouched copy of the original source artifact.
- Do not commit ISOs, XEX files, extracted proprietary assets, keys, or decrypted proprietary content.
- Record derived executable paths and hashes here before using them for ReXGlue analysis or generation.
