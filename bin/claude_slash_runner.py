#!/usr/bin/env python3
"""
Minimal local slash-command runner for `.claude/commands`.

Features:
- Lists available commands by filename and discovered usage_command blocks
- Resolves and "runs" a command string like "/dagrunner foo" by locating the
  corresponding definition file and printing its key sections for human use

Note: This runner does not execute actions inside the command files. It simply
surfaces intent, usage, and related metadata to aid local workflows.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
COMMANDS_DIR = ROOT / ".claude" / "commands"


def iter_command_files() -> List[Path]:
    exts = (".md",)
    if not COMMANDS_DIR.exists():
        return []
    files: List[Path] = []
    for p in COMMANDS_DIR.rglob("*"):
        if p.is_file() and p.suffix in exts:
            files.append(p)
    return sorted(files)


def extract_usage_block(text: str) -> Optional[str]:
    # Capture a YAML-like key `usage_command:` with an indented block, or a section with a heading
    # Strategy: find line starting with `usage_command:`; capture following indented lines until blank
    m = re.search(r"^usage_command:\s*\|?\s*$", text, flags=re.MULTILINE)
    if not m:
        return None
    start = m.end()
    # Collect subsequent indented lines
    lines = []
    for line in text[start:].splitlines():
        if not line.strip():
            # Allow empty line within block; break only if next non-empty not indented
            # We'll append empties and continue; stopping rule handled later
            lines.append(line)
            continue
        if re.match(r"^[ \t]", line):
            lines.append(line)
        else:
            break
    # Trim common indentation
    if not lines:
        return None
    # Remove trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()
    # Determine minimal indent across non-empty lines
    indents = [len(re.match(r"^[ \t]*", ln).group(0)) for ln in lines if ln.strip()]
    base = min(indents) if indents else 0
    block = "\n".join(ln[base:] if len(ln) >= base else ln for ln in lines)
    return block.strip() or None


def extract_meta(text: str) -> Dict[str, str]:
    meta: Dict[str, str] = {}
    # Best-effort extraction of meta.name and meta.version and purpose block
    # 1) Try YAML front-matter style delimited by --- ... ---
    fm = None
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            fm = text[4:end]
    # Search in front matter or whole text
    scope = fm if fm else text
    m_name = re.search(r"^\s*name:\s*\"?([^\"\n]+)\"?\s*$", scope, flags=re.MULTILINE)
    if m_name:
        meta["name"] = m_name.group(1).strip()
    else:
        # Try meta: name inside nested YAML
        m2 = re.search(r"^meta:\s*(?:\n|\r\n)([\s\S]*?)\n\S", text, flags=re.MULTILINE)
        if m2:
            inner = m2.group(1)
            m3 = re.search(r"^\s*name:\s*\"?([^\"\n]+)\"?\s*$", inner, flags=re.MULTILINE)
            if m3:
                meta["name"] = m3.group(1).strip()
    m_ver = re.search(r"^\s*version:\s*\"?([^\"\n]+)\"?\s*$", scope, flags=re.MULTILINE)
    if m_ver:
        meta["version"] = m_ver.group(1).strip()

    # purpose: may be a pipe-block
    m_purpose = re.search(r"^\s*purpose:\s*(\|?>)?\s*$", scope, flags=re.MULTILINE)
    if m_purpose:
        start = m_purpose.end()
        lines = []
        for line in scope[start:].splitlines():
            if not line.strip():
                lines.append(line)
                continue
            if re.match(r"^[ \t]", line):
                lines.append(line)
            else:
                break
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            indents = [len(re.match(r"^[ \t]*", ln).group(0)) for ln in lines if ln.strip()]
            base = min(indents) if indents else 0
            block = "\n".join(ln[base:] if len(ln) >= base else ln for ln in lines)
            meta["purpose"] = block.strip()
    return meta


def derive_command_names(path: Path, usage_block: Optional[str]) -> List[str]:
    names: List[str] = []
    # From usage_block: lines like "/dag-debug-enhanced ..." — take token after '/'
    if usage_block:
        for line in usage_block.splitlines():
            line = line.strip()
            if line.startswith("/"):
                cmd = line.split()[0].strip()
                # remove options in same token if any (rare)
                cmd = cmd.split("#")[0].strip()
                names.append(cmd)
    # From filename
    stem = path.stem
    names.append(f"/{stem}")
    # Deduplicate preserving order
    seen = set()
    out: List[str] = []
    for n in names:
        if n not in seen:
            out.append(n)
            seen.add(n)
    return out


def build_index() -> Dict[str, Dict[str, object]]:
    index: Dict[str, Dict[str, object]] = {}
    for p in iter_command_files():
        text = p.read_text(encoding="utf-8", errors="ignore")
        usage = extract_usage_block(text)
        meta = extract_meta(text)
        names = derive_command_names(p, usage)
        record = {"path": p, "usage": usage, "meta": meta}
        for name in names:
            index.setdefault(name, record)
    return index


def cmd_list(args: argparse.Namespace) -> None:
    index = build_index()
    if not index:
        print("No commands found under .claude/commands.")
        return
    # Group by unique path to avoid duplicates due to aliases
    seen_paths: Dict[Path, List[str]] = {}
    for key, rec in index.items():
        seen_paths.setdefault(rec["path"], []).append(key)
    for path, aliases in sorted(seen_paths.items(), key=lambda kv: str(kv[0])):
        meta = build_index()[aliases[0]]["meta"]  # reusing index to get meta
        name = meta.get("name") if isinstance(meta, dict) else None
        print(f"- {', '.join(sorted(set(aliases)))} -> {path}")
        if name:
            print(f"  name: {name}")


def resolve_command_token(s: str) -> Tuple[str, List[str]]:
    s = s.strip()
    if not s:
        raise ValueError("Empty command")
    parts = s.split()
    token = parts[0]
    if not token.startswith('/'):
        raise ValueError("Command must start with '/' (e.g., /dagrunner)")
    return token, parts[1:]


def cmd_run(args: argparse.Namespace) -> None:
    token, rest = resolve_command_token(args.command)
    index = build_index()
    # Try exact, then relaxed matching: e.g., '/dagrunner' vs '/dag-debug-enhanced'
    rec = index.get(token)
    if not rec:
        # Try fallback: same token without dashes/underscores
        norm = token.replace('-', '').replace('_', '')
        for k in index.keys():
            knorm = k.replace('-', '').replace('_', '')
            if knorm == norm:
                rec = index[k]
                break
    if not rec:
        print(f"Command not found: {token}")
        print("Tip: Use 'list' to see available commands.")
        return
    path: Path = rec["path"]  # type: ignore[assignment]
    usage: Optional[str] = rec.get("usage")  # type: ignore[assignment]
    meta: Dict[str, str] = rec.get("meta", {})  # type: ignore[assignment]
    print(f"Command: {token}")
    if rest:
        print(f"Args: {' '.join(rest)}")
    print(f"Source: {path}")
    if meta.get("name"):
        print(f"Name: {meta['name']}")
    if meta.get("version"):
        print(f"Version: {meta['version']}")
    if meta.get("purpose"):
        print("Purpose:\n" + meta["purpose"])  # already multiline
    if usage:
        print("\nUsage:\n" + usage)
    else:
        # Fallback: show first 40 lines as a hint
        text = path.read_text(encoding="utf-8", errors="ignore")
        head = "\n".join(text.splitlines()[:40])
        print("\nUsage: (not declared)\n---\n" + head + "\n---")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local runner for .claude/commands")
    sub = parser.add_subparsers(dest="sub")

    p_list = sub.add_parser("list", help="List available commands")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Run a command by string, e.g., '/dagrunner foo'")
    p_run.add_argument("command", help="Slash command with optional args, quoted if needed")
    p_run.set_defaults(func=cmd_run)

    # Convenience: if first argument looks like a slash command, treat as run
    import sys
    if len(sys.argv) >= 2 and sys.argv[1].startswith('/'):
        ns = argparse.Namespace(sub="run", command=" ".join(sys.argv[1:]))
        return cmd_run(ns)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()

