# Asset Ledger

| Artifact | Path | SHA-256 | Size | Status | Notes |
|---|---|---|---:|---|---|
| Canonical source ISO | `D:\360RexGlue\TheOutFit\theoutfit.iso` | `9112A8E01719FC52749D0A735CD0CF44CE11C9F575714F0467B4EE30F7F5353A` | 7,834,892,288 bytes | Confirmed | User confirmed this lawful ISO is the source artifact for the project. Do not commit it. |
| Extracted entrypoint XEX | `D:\360RexGlue\TheOutFit\assets\game_files\default.xex` | `1BD7C232574681D51865C40383581F4157592991998BC6CE085E24CE38325654` | 9,056,256 bytes | Confirmed | Extracted from the canonical ISO with `extract-xiso`; used as ReXGlue `entrypoint.file_path`. Do not commit it. |
| Derived loose locale icon map | `D:\360RexGlue\TheOutFit\assets\game_files\Common\WW2\Locale\English\IconMappings.map` | `439F7F8ED036EB6AA6438585BD74EBA1573DE507088B69C3B6CF2D23B20D1A64` | 972 bytes | Local derived asset | Extracted locally from the canonical `XModLoc.sga` payload after runtime evidence showed a direct loose-file fallback for `D:\common\ww2\locale\English\IconMappings.map`. This file is proprietary derived content under ignored `assets/game_files/`; do not commit it. |
| Frontend archive used during first frame | `D:\360RexGlue\TheOutFit\assets\game_files\ingame_ui.XZP` | `200A29F01A3FEDC6BE9F4E43C1335EF013459AC17C74015B8D77E3078F6B4084` | 754,071 bytes | Confirmed local input | Runtime trace after the switch/function fixes opened and read this archive before repeated GPU resolve progress and first rendered frame capture. It remains proprietary content under ignored `assets/game_files/`; do not commit it. |

## Policy
- Keep an untouched copy of the original source artifact.
- Do not commit ISOs, XEX files, extracted proprietary assets, keys, or decrypted proprietary content.
- Record derived executable paths and hashes here before using them for ReXGlue analysis or generation.
