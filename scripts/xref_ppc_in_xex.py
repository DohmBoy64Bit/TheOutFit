"""Scan retail XEX .text for PPC xrefs (direct bl/bcl) and indirect bctr hints.

Read-only analysis of assets/game_files/default.xex (or --xex path).
Uses lief for VA mapping and Capstone for Xenon PPC (32-bit BE).

Usage:
  python xref_ppc_in_xex.py --xex assets/default.xex --xref-to 0x8270DEF0
  python xref_ppc_in_xex.py --xex assets/default.xex --xref-to 0x8270D720 0x826E43A8
  python xref_ppc_in_xex.py --xex assets/default.xex --disasm-func 0x8270DEF0 --func-max 256
  python xref_ppc_in_xex.py --xex assets/default.xex --scan-bctr 0x8270DEF0 0x8270D720
  python xref_ppc_in_xex.py --xex assets/default.xex --xref-from-range 0x8240AA00 0x8240AC00
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_PPC, CS_MODE_32, CS_MODE_BIG_ENDIAN

try:
    from xex2_util import extract_xex_image, va_to_offset
except ImportError:
    extract_xex_image = None  # type: ignore
    va_to_offset = None  # type: ignore

REX_IMAGE_BASE = 0x82000000
REX_CODE_BASE = 0x82140000
REX_CODE_SIZE = 0xBAE27C


def parse_hex(s: str) -> int:
    return int(s, 0)


def find_bytes_for_va(bin_, raw: bytes, va: int, nbytes: int) -> bytes | None:
    if bin_ is not None and hasattr(bin_, "sections"):
        for s in bin_.sections:
            sva = s.virtual_address
            svsize = s.virtual_size
            soff = s.offset
            srawlen = len(s.content)
            if sva <= va < sva + max(svsize, srawlen):
                file_off = soff + (va - sva)
                if 0 <= file_off and file_off + nbytes <= len(raw):
                    return raw[file_off : file_off + nbytes]
    if REX_CODE_BASE <= va < REX_CODE_BASE + REX_CODE_SIZE:
        off = va - REX_CODE_BASE
        if off + nbytes <= len(raw):
            return raw[off : off + nbytes]
    return None


def load_code_blob(xex_path: Path, code_base: int, code_size: int) -> tuple[bytes, int] | None:
    """Return (code_bytes, image_base) from decrypted/decompressed XEX2 image."""
    if extract_xex_image is None:
        return None
    try:
        image, image_base = extract_xex_image(xex_path)
    except Exception as exc:
        print(f"WARN: XEX extract failed: {exc}", file=sys.stderr)
        return None
    off = va_to_offset(image, image_base, code_base, code_base)
    if off is None:
        print(f"WARN: code_base 0x{code_base:08X} not in image (base 0x{image_base:08X})", file=sys.stderr)
        return None
    return image[off : off + code_size], code_base


def parse_branch_target(mnemonic: str, op_str: str) -> int | None:
    m = re.search(r"0x([0-9a-fA-F]+)", op_str)
    if m:
        return int(m.group(1), 16)
    return None


def decode_bl_target(caller_va: int, word: int) -> int:
    """PPC I-form branch (opcode 18): bl / b / bla."""
    aa = (word >> 1) & 1
    li = word & 0x03FFFFFC
    if li & 0x02000000:
        li -= 0x04000000
    if aa:
        return li & 0xFFFFFFFF
    return (caller_va + li) & 0xFFFFFFFF


def decode_bcl_target(caller_va: int, word: int) -> int | None:
    """PPC B-form (opcode 16) with LK=1: bcl."""
    if (word >> 26) != 16 or ((word >> 21) & 1) == 0:
        return None
    aa = (word >> 1) & 1
    bd = word & 0x0000FFFC
    if bd & 0x00008000:
        bd -= 0x00010000
    if aa:
        return bd & 0xFFFFFFFF
    return (caller_va + bd) & 0xFFFFFFFF


def scan_bl_raw_to_targets(
    code: bytes, base_va: int, targets: set[int]
) -> list[tuple[int, str, str, int]]:
    """Scan code for direct bl/bcl via opcode decode (robust on full XEX image)."""
    hits: list[tuple[int, str, str, int]] = []
    for off in range(0, len(code) - 3, 4):
        word = int.from_bytes(code[off : off + 4], "big")
        op = word >> 26
        va = base_va + off
        tgt: int | None = None
        mnem = ""
        if op == 18:
            tgt = decode_bl_target(va, word)
            mnem = "bla" if (word >> 1) & 1 else "bl"
        elif op == 16:
            tgt = decode_bcl_target(va, word)
            if tgt is not None:
                mnem = "bcl"
        if tgt is not None and tgt in targets:
            hits.append((va, mnem, f"0x{tgt:08X}", tgt))
    return hits


def scan_bl_to_targets(
    md: Cs, code: bytes, base_va: int, targets: set[int]
) -> list[tuple[int, str, str, int]]:
    """Return list of (caller_va, mnemonic, op_str, target_va) for branch-to-target."""
    return scan_bl_raw_to_targets(code, base_va, targets)


def scan_range_calls(
    md: Cs, code: bytes, base_va: int, lo: int, hi: int
) -> list[tuple[int, str, str, int | None]]:
    """List all bl/bcl in [lo, hi] and their targets."""
    out: list[tuple[int, str, str, int | None]] = []
    start_off = max(0, lo - base_va)
    end_off = min(len(code), hi - base_va)
    sub = code[start_off:end_off]
    sub_base = base_va + start_off
    for insn in md.disasm(sub, sub_base):
        if insn.mnemonic in ("bl", "bcl", "bcl.", "bl."):
            tgt = parse_branch_target(insn.mnemonic, insn.op_str)
            out.append((insn.address, insn.mnemonic, insn.op_str, tgt))
    return out


def scan_bctr_sites(
    md: Cs, code: bytes, base_va: int, watch: set[int]
) -> list[tuple[int, str, str, list[int]]]:
    """Find mtctr/bctr sequences; collect lis/ori/addi immediates before bctr."""
    results: list[tuple[int, str, str, list[int]]] = []
    insns = list(md.disasm(code, base_va))
    for i, insn in enumerate(insns):
        if insn.mnemonic != "bctr" and insn.mnemonic != "bctrl":
            continue
        imms: list[int] = []
        for j in range(max(0, i - 8), i):
            prev = insns[j]
            for part in prev.op_str.replace(",", " ").split():
                if part.startswith("0x"):
                    try:
                        imms.append(int(part, 16))
                    except ValueError:
                        pass
        if any((v & ~0xFFFF) in watch or (v | 0x80000000) in watch for v in imms):
            results.append((insn.address, insn.mnemonic, insn.op_str, imms[-6:]))
        elif any(w & 0xFFFF0000 == (v & 0xFFFF0000) for w in watch for v in imms if v > 0x10000):
            results.append((insn.address, insn.mnemonic, insn.op_str, imms[-6:]))
    return results


def disasm_function(
    md: Cs, xex_path: Path, loaded: tuple[bytes, int] | None, entry: int, max_insns: int
) -> list[str]:
    lines: list[str] = []
    if loaded is None:
        return [f"(could not load XEX image)"]
    code, image_base = loaded
    off = va_to_offset(code, image_base, REX_CODE_BASE, entry) if va_to_offset else None
    if off is None:
        return [f"(could not read 0x{entry:08X})"]
    chunk = code[off : off + max_insns * 4]
    count = 0
    for insn in md.disasm(chunk, entry):
        lines.append(f"0x{insn.address:08X}: {insn.bytes.hex():<8} {insn.mnemonic:<8} {insn.op_str}")
        count += 1
        if count >= max_insns:
            break
        if insn.mnemonic in ("blr",) and count > 4:
            break
    return lines


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="PPC xref scanner for PDZ XEX")
    p.add_argument("--xex", required=True, type=Path)
    p.add_argument("--code-base", type=parse_hex, default=REX_CODE_BASE)
    p.add_argument("--code-size", type=parse_hex, default=REX_CODE_SIZE)
    p.add_argument(
        "--xref-to",
        action="append",
        default=[],
        metavar="VA",
        help="find bl callers of VA (repeat flag or comma-separated)",
    )
    p.add_argument("--xref-from-range", nargs=2, metavar=("LO", "HI"), help="list bl in VA range")
    p.add_argument("--disasm-func", type=parse_hex, help="disassemble from entry VA")
    p.add_argument("--func-max", type=int, default=128, help="max insns for --disasm-func")
    p.add_argument("--scan-bctr", action="append", default=[], help="watch VAs near bctr")
    p.add_argument("--markdown", type=Path, help="append summary markdown to file")
    args = p.parse_args(argv)

    if not args.xex.is_file():
        print(f"ERROR: xex not found: {args.xex}", file=sys.stderr)
        return 2

    md = Cs(CS_ARCH_PPC, CS_MODE_32 | CS_MODE_BIG_ENDIAN)
    md.detail = False

    loaded = load_code_blob(args.xex, args.code_base, args.code_size)
    if loaded is None:
        print("ERROR: could not load code section", file=sys.stderr)
        return 2
    code, base_va = loaded

    print(f"XEX: {args.xex}")
    print(f"Code: VA 0x{base_va:08X} size 0x{len(code):X} ({len(code)} bytes)")
    print()

    md_lines: list[str] = []

    if args.disasm_func is not None:
        print(f"=== disasm @ 0x{args.disasm_func:08X} (max {args.func_max}) ===")
        for line in disasm_function(md, args.xex, loaded, args.disasm_func, args.func_max):
            print(f"  {line}")
        print()
        md_lines.append(f"### disasm `0x{args.disasm_func:08X}`\n\n```\n")
        md_lines.extend(disasm_function(md, args.xex, loaded, args.disasm_func, min(args.func_max, 64)))
        md_lines.append("```\n")

    xref_to_list: list[str] = []
    for item in args.xref_to:
        xref_to_list.extend(x.strip() for x in item.split(",") if x.strip())

    if xref_to_list:
        targets = {parse_hex(t) for t in xref_to_list}
        print("=== direct bl/bcl xrefs TO target(s) ===")
        hits = scan_bl_to_targets(md, code, base_va, targets)
        by_target: dict[int, list] = {t: [] for t in targets}
        for h in hits:
            by_target[h[3]].append(h)
        for t in sorted(targets):
            print(f"\n-- 0x{t:08X} ({len(by_target[t])} callers) --")
            md_lines.append(f"\n### `bl` callers of `0x{t:08X}` ({len(by_target[t])})\n\n")
            if not by_target[t]:
                print("  (none)")
                md_lines.append("(no direct `bl` in scanned code)\n")
                continue
            md_lines.append("| caller VA | insn | operand |\n|-----------|------|--------|\n")
            for caller, mnem, ops, _ in sorted(by_target[t]):
                print(f"  0x{caller:08X}: {mnem} {ops}")
                md_lines.append(f"| `0x{caller:08X}` | {mnem} | `{ops}` |\n")

    if args.xref_from_range:
        lo = parse_hex(args.xref_from_range[0])
        hi = parse_hex(args.xref_from_range[1])
        print(f"=== bl/bcl in range [0x{lo:08X}, 0x{hi:08X}) ===")
        calls = scan_range_calls(md, code, base_va, lo, hi)
        md_lines.append(f"\n### `bl` sites in `0x{lo:08X}`..`0x{hi:08X}` ({len(calls)})\n\n")
        md_lines.append("| VA | insn | target |\n|----|------|--------|\n")
        for va, mnem, ops, tgt in calls[:200]:
            ts = f"`0x{tgt:08X}`" if tgt is not None else "?"
            print(f"  0x{va:08X}: {mnem} {ops}")
            md_lines.append(f"| `0x{va:08X}` | {mnem} | {ts} |\n")
        if len(calls) > 200:
            print(f"  ... ({len(calls) - 200} more)")
        print(f"total: {len(calls)}")
        print()

    if args.scan_bctr:
        watch = {parse_hex(t) for t in args.scan_bctr}
        print("=== bctr sites with nearby address material (heuristic) ===")
        bctr_hits = scan_bctr_sites(md, code, base_va, watch)
        md_lines.append("\n### Indirect `bctr` hints (heuristic)\n\n")
        for va, mnem, ops, imms in bctr_hits[:80]:
            print(f"  0x{va:08X}: {mnem} {ops}  imms={imms}")
            md_lines.append(f"- `0x{va:08X}` imms `{imms}`\n")
        print(f"total bctr hints: {len(bctr_hits)}")
        print()

    if args.markdown and md_lines:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        with args.markdown.open("a", encoding="utf-8") as f:
            f.write("".join(md_lines))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
