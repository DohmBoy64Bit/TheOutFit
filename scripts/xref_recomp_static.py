"""Static call graph from generated recomp (derived from XEX by rexglue codegen).

Scans generated/default/perfectdarkzero_recomp.*.cpp for sub_* calls.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

CALL_RE = re.compile(r"\bsub_([0-9A-Fa-f]+)\(ctx")
BL_COMMENT_RE = re.compile(r"//\s*bl\s+0x([0-9A-Fa-f]+)", re.I)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gen-dir", type=Path, default=Path("generated/default"))
    p.add_argument("--target", action="append", required=True, help="hex VA without sub_")
    p.add_argument("--markdown", type=Path, default=None)
    args = p.parse_args()

    targets: set[str] = set()
    for item in args.target:
        for part in item.split(","):
            part = part.strip().lower().removeprefix("0x")
            if part:
                targets.add(part)
    hits: dict[str, list[tuple[str, int, str]]] = {t: [] for t in targets}

    for cpp in sorted(args.gen_dir.glob("perfectdarkzero_recomp.*.cpp")):
        text = cpp.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            m = CALL_RE.search(line)
            if m:
                va = m.group(1).lower()
                if va in targets:
                    hits[va].append((cpp.name, i, line.strip()[:100]))
            m2 = BL_COMMENT_RE.search(line)
            if m2:
                va = m2.group(1).lower()
                if va in targets:
                    hits[va].append((cpp.name, i, f"(bl comment) {line.strip()[:80]}"))

    lines_out: list[str] = []
    for t in sorted(targets, key=lambda x: int(x, 16)):
        print(f"\n=== sub_{t.upper()} ({len(hits[t])} static call sites) ===")
        lines_out.append(f"\n### `sub_{t.upper()}` — {len(hits[t])} static sites in generated\n\n")
        if not hits[t]:
            print("  (none)")
            lines_out.append("(no `sub_*` or `// bl` in generated recomp)\n")
            continue
        lines_out.append("| file | line | snippet |\n|------|------|--------|\n")
        for name, ln, snip in hits[t][:80]:
            print(f"  {name}:{ln}: {snip}")
            lines_out.append(f"| `{name}` | {ln} | `{snip}` |\n")
        if len(hits[t]) > 80:
            print(f"  ... {len(hits[t]) - 80} more")
            lines_out.append(f"\n({len(hits[t]) - 80} more)\n")

    if args.markdown:
        args.markdown.write_text("".join(lines_out), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
