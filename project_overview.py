# -*- coding: utf-8 -*-
"""
Java Project Overview Generator
Quickly understand the skeleton of a Java project.

How to run:
  1. Set PROJECT_DIR below to your Java project folder
  2. Open Anaconda Prompt, cd to this script's folder, then run:
         python project_overview.py
  3. A file called project_overview.md will be created in the same folder.
     Upload it to Copilot to give it a high-level understanding of the project.

Uses Python standard library only — no extra packages needed.
Note: Parsing is heuristic (regex-based). Works well for most code,
      but may occasionally miss or misread edge cases.
"""

import re
import sys
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION (edit here) ====================
PROJECT_DIR = r"C:\Users\YourName\path\to\java\project"   # <- change this
OUTPUT_FILE = "project_overview.md"

# Directories to skip (compiled output, dependencies, version history, etc.)
IGNORE_DIRS = {
    "target", "build", "bin", "out", "dist", "classes",
    ".git", ".idea", ".settings", ".gradle", ".mvn", "node_modules",
}

# Whether to list public/protected method signatures for each class.
# False = show only the method count (shorter output, recommended to start)
# True  = list full signatures (more detail, but output can get large)
SHOW_METHODS = False
# ===================================================================


def read_text(path: Path) -> str:
    """Try multiple encodings to handle Chinese comments without errors."""
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def strip_comments(code: str) -> str:
    """Roughly remove comments and string literals to reduce regex false positives."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)   # block comments /* */
    code = re.sub(r"//[^\n]*", " ", code)                      # line comments //
    code = re.sub(r'"(\\.|[^"\\])*"', '""', code)              # string literals
    return code


def analyze_java(path: Path) -> dict:
    raw = read_text(path)
    code = strip_comments(raw)
    info = {"lines": raw.count("\n") + 1, "package": None,
            "types": [], "has_main": False, "methods": []}

    m = re.search(r"\bpackage\s+([\w.]+)\s*;", code)
    if m:
        info["package"] = m.group(1)

    # Top-level types (class / interface / enum / record) and their inheritance
    for m in re.finditer(
        r"\b(?:public\s+|abstract\s+|final\s+|sealed\s+|non-sealed\s+)*"
        r"(class|interface|enum|record)\s+(\w+)([^{]*)\{",
        code,
    ):
        kind, name, rest = m.group(1), m.group(2), m.group(3)
        ext = re.search(r"\bextends\s+([\w.<>,\s]+?)(?:\bimplements\b|\{|$)", rest)
        impl = re.search(r"\bimplements\s+([\w.<>,\s]+)", rest)
        info["types"].append({
            "kind": kind,
            "name": name,
            "extends": " ".join(ext.group(1).split()) if ext else None,
            "implements": " ".join(impl.group(1).split()) if impl else None,
        })

    if re.search(r"\bpublic\s+static\s+void\s+main\s*\(", code):
        info["has_main"] = True

    # public / protected methods (heuristic)
    for m in re.finditer(
        r"\b(public|protected)\s+"
        r"(?:static\s+|final\s+|abstract\s+|synchronized\s+|native\s+|default\s+)*"
        r"([\w.<>\[\],\s]+?\s+)?(\w+)\s*\(([^)]*)\)\s*"
        r"(?:throws\s+[\w.,\s]+)?[{;]",
        code,
    ):
        mname = m.group(3)
        if mname in {"if", "for", "while", "switch", "catch", "synchronized", "return", "new"}:
            continue
        ret = (m.group(2) or "").strip()
        args = " ".join(m.group(4).split())
        sig = " ".join(f"{m.group(1)} {ret} {mname}({args})".split())
        info["methods"].append(sig)

    return info


def build_tree(rel_paths):
    tree = {}
    for rp in rel_paths:
        node = tree
        for part in rp.parts:
            node = node.setdefault(part, {})
    return tree


def render_tree(node, prefix=""):
    lines = []
    # Directories first, then files; each group sorted alphabetically
    items = sorted(node.items(), key=lambda kv: (len(kv[1]) == 0, kv[0].lower()))
    for i, (name, child) in enumerate(items):
        last = (i == len(items) - 1)
        lines.append(prefix + ("└── " if last else "├── ") + name)
        if child:
            lines.extend(render_tree(child, prefix + ("    " if last else "│   ")))
    return lines


def main():
    root = Path(PROJECT_DIR)
    if not root.is_dir():
        print(f"Directory not found: {root}\nPlease update PROJECT_DIR at the top of this script.")
        sys.exit(1)

    java_files = []
    for p in root.rglob("*.java"):
        if any(part in IGNORE_DIRS for part in p.relative_to(root).parts):
            continue
        java_files.append(p)

    if not java_files:
        print("No .java files found. Please check that PROJECT_DIR points to the right folder.")
        sys.exit(1)

    analyzed = []
    for p in sorted(java_files):
        rel = p.relative_to(root)
        try:
            info = analyze_java(p)
        except Exception as e:
            info = {"lines": 0, "package": None, "types": [],
                    "has_main": False, "methods": [], "error": str(e)}
        analyzed.append((rel, info))

    total_lines = sum(i["lines"] for _, i in analyzed)
    packages = sorted({i["package"] or "(default package)" for _, i in analyzed})
    entry_points = [(rel, i) for rel, i in analyzed if i["has_main"]]
    largest = sorted(analyzed, key=lambda ri: ri[1]["lines"], reverse=True)[:15]

    out = []
    out.append(f"# Project Overview: {root.name}\n")
    out.append(f"- Project path: `{root}`")
    out.append(f"- Generated: {datetime.now():%Y-%m-%d %H:%M}")
    out.append(f"- Java source files: **{len(analyzed)}**")
    out.append(f"- Total source lines: **{total_lines:,}**")
    out.append(f"- Packages: **{len(packages)}**\n")

    out.append("## 1. Entry Points (files containing a main method)")
    if entry_points:
        for rel, _ in entry_points:
            out.append(f"- `{rel.as_posix()}`")
    else:
        out.append("- No main method found. This may be a library or web project "
                   "whose entry point is defined in a framework or config file.")
    out.append("")

    out.append("## 2. Largest Source Files (usually where core logic lives)")
    out.append("| Lines | File |")
    out.append("|---:|:---|")
    for rel, i in largest:
        out.append(f"| {i['lines']:,} | `{rel.as_posix()}` |")
    out.append("")

    out.append("## 3. Directory Structure (.java files only)")
    out.append("```")
    out.append(root.name + "/")
    out.extend(render_tree(build_tree([rel for rel, _ in analyzed])))
    out.append("```\n")

    out.append("## 4. Classes by Package")
    by_pkg = {}
    for rel, i in analyzed:
        by_pkg.setdefault(i["package"] or "(default package)", []).append((rel, i))
    for pkg in sorted(by_pkg):
        out.append(f"\n### 📦 {pkg}")
        for rel, i in sorted(by_pkg[pkg], key=lambda x: x[0].as_posix()):
            if not i["types"]:
                out.append(f"- `{rel.name}` ({i['lines']} lines)")
                continue
            for t in i["types"]:
                rel_parts = []
                if t["extends"]:
                    rel_parts.append(f"extends {t['extends']}")
                if t["implements"]:
                    rel_parts.append(f"implements {t['implements']}")
                tail = ("  —  " + ", ".join(rel_parts)) if rel_parts else ""
                main_flag = "  ▶ entry point" if i["has_main"] else ""
                out.append(f"- **{t['kind']} {t['name']}**{tail}"
                           f"  ·  {len(i['methods'])} public method(s){main_flag}")
            if SHOW_METHODS and i["methods"]:
                for sig in i["methods"]:
                    out.append(f"    - `{sig}`")
    out.append("")

    Path(OUTPUT_FILE).write_text("\n".join(out), encoding="utf-8")
    print(f"Done! Output written to: {OUTPUT_FILE}")
    print(f"  {len(analyzed)} Java file(s), {total_lines:,} total lines")
    print(f"  Upload {OUTPUT_FILE} to Copilot to give it an overview of the project structure.")


if __name__ == "__main__":
    main()
