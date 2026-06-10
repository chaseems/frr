"""
Java Source Concatenator
Merges all .java source files and config/resource files (XML, DTD,
properties, YAML, etc.) in a project into one text file so the full
codebase can be uploaded to Copilot in one go.

How to run:
  1. Set PROJECT_DIR below to your Java project folder
  2. Open Anaconda Prompt, cd to this script's folder, then run:
         python concat_java.py
  3. all_java_code.txt (or split part files) will be created in the
     same folder. Upload the file(s) to Copilot.

Uses Python standard library only — no extra packages needed.
"""

import sys
from pathlib import Path

# ==================== CONFIGURATION (edit here) ====================
PROJECT_DIR = r"C:\Users\YourName\path\to\java\project"   # <- change this
OUTPUT_FILE = "all_java_code.txt"

# Directories to skip (compiled output, dependencies, version history, etc.)
IGNORE_DIRS = {
    "target", "build", "bin", "out", "dist", "classes",
    ".git", ".idea", ".settings", ".gradle", ".mvn", "node_modules",
}

# Whether to include test code (files whose path contains "test").
# Set to False to help Copilot focus on business logic only.
INCLUDE_TESTS = True

# Config/resource file extensions to include alongside .java files.
# Remove any entry here if you want to exclude that file type.
EXTRA_EXTENSIONS = {
    ".xml",          # Maven pom.xml, Spring config, custom XML config
    ".dtd",          # XML structure definitions referenced by XML files
    ".properties",   # Java .properties config files
    ".yml",          # YAML config (e.g. Spring Boot application.yml)
    ".yaml",         # same as above, alternate extension
    ".json",         # JSON config files
    ".sql",          # SQL scripts sometimes bundled in resources
}

# Number of output parts. Copilot allows up to 3 file uploads per conversation.
# 1 = single output file. If the file is too large, change to 2 or 3 to split evenly.
SPLIT_PARTS = 1
# ===================================================================

# If the total output exceeds this many characters, a warning is printed.
WARN_CHARS = 600_000


def read_text(path: Path) -> str:
    """Try multiple encodings to handle Chinese comments without errors."""
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def is_test(rel: Path) -> bool:
    parts = [p.lower() for p in rel.parts]
    return any("test" in p for p in parts)


def collect_files(root: Path) -> tuple[list, list]:
    """
    Walk the project tree and return two sorted lists:
      java_files  — list of (rel_path, abs_path) for .java files
      extra_files — list of (rel_path, abs_path) for config/resource files
    Both lists skip IGNORE_DIRS.
    """
    all_extensions = {".java"} | EXTRA_EXTENSIONS
    java_files, extra_files = [], []

    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() not in all_extensions:
            continue
        if not INCLUDE_TESTS and is_test(rel):
            continue

        if p.suffix.lower() == ".java":
            java_files.append((rel, p))
        else:
            extra_files.append((rel, p))

    return java_files, extra_files


def make_block(rel: Path, p: Path) -> str:
    """Format one file as a labelled text block."""
    text = read_text(p)
    sep = "=" * 78
    return (f"{sep}\n"
            f"// FILE: {rel.as_posix()}\n"
            f"{sep}\n"
            f"{text}\n\n")


def split_blocks(blocks: list[str], n: int, output_file: str) -> dict[str, str]:
    """Split blocks into n roughly equal parts; return {filename: content}."""
    if n == 1:
        return {output_file: "".join(blocks)}

    total = sum(len(b) for b in blocks)
    target = total / n
    parts, cur, cur_size = [], [], 0
    for b in blocks:
        if cur and cur_size + len(b) > target and len(parts) < n - 1:
            parts.append("".join(cur))
            cur, cur_size = [], 0
        cur.append(b)
        cur_size += len(b)
    if cur:
        parts.append("".join(cur))

    stem = Path(output_file).stem
    suffix = Path(output_file).suffix or ".txt"
    return {f"{stem}_part{idx}{suffix}": txt
            for idx, txt in enumerate(parts, start=1)}


def main():
    root = Path(PROJECT_DIR)
    if not root.is_dir():
        print(f"Directory not found: {root}")
        print("Please update PROJECT_DIR at the top of this script.")
        sys.exit(1)

    java_files, extra_files = collect_files(root)

    if not java_files and not extra_files:
        print("No source files found. Please check that PROJECT_DIR points to the right folder.")
        sys.exit(1)

    # --- Build content ---
    # Section 1: Java source files
    java_blocks, java_lines = [], 0
    for rel, p in java_files:
        text = read_text(p)
        java_lines += text.count("\n") + 1
        java_blocks.append(make_block(rel, p))

    # Section 2: Config / resource files
    extra_blocks, extra_lines = [], 0
    for rel, p in extra_files:
        text = read_text(p)
        extra_lines += text.count("\n") + 1
        extra_blocks.append(make_block(rel, p))

    total_files = len(java_files) + len(extra_files)
    total_lines = java_lines + extra_lines

    section_java  = "=" * 78 + "\n// SECTION: JAVA SOURCE FILES\n" + "=" * 78 + "\n\n"
    section_extra = "=" * 78 + "\n// SECTION: CONFIG / RESOURCE FILES\n" + "=" * 78 + "\n\n"

    all_blocks = (
        [section_java]  + java_blocks +
        [section_extra] + extra_blocks
    )

    # --- Split and write ---
    n = max(1, SPLIT_PARTS)
    outputs = split_blocks(all_blocks, n, OUTPUT_FILE)
    total_chars = sum(len(v) for v in outputs.values())

    for name, content in outputs.items():
        header = (f"// Generated by concat_java.py\n"
                  f"// Project: {root.name}  |  "
                  f"{len(java_files)} Java file(s), "
                  f"{len(extra_files)} config/resource file(s), "
                  f"{total_lines:,} lines total\n\n")
        Path(name).write_text(header + content, encoding="utf-8")

    # --- Summary ---
    print(f"Done! {total_files} file(s) merged, "
          f"{total_lines:,} lines, {total_chars:,} characters.")
    print(f"  Java source files    : {len(java_files)}"
          f"  ({java_lines:,} lines)")
    print(f"  Config/resource files: {len(extra_files)}"
          f"  ({extra_lines:,} lines)")
    if extra_files:
        # List the config files so the user can see what was picked up
        by_ext: dict[str, list] = {}
        for rel, _ in extra_files:
            by_ext.setdefault(rel.suffix.lower(), []).append(rel.name)
        for ext, names in sorted(by_ext.items()):
            print(f"    {ext}: {', '.join(names)}")
    print()
    for name in outputs:
        size_kb = Path(name).stat().st_size / 1024
        print(f"  Output: {name}  ({size_kb:,.0f} KB)")

    if n == 1 and total_chars > WARN_CHARS:
        print("\nWarning: the output file is large and Copilot may not read it all.")
        print("  Try setting SPLIT_PARTS to 2 or 3 and re-running,")
        print("  or set INCLUDE_TESTS = False to exclude test files.")


if __name__ == "__main__":
    main()
