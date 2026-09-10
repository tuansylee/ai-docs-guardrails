#!/usr/bin/env python3
"""Generate an llms.txt-style map of a docs set: read the map, don't crawl the tree.

For every Markdown file it harvests the frontmatter `description`, writes a sorted
table into INDEX.md between MAP:AUTO markers, lists files marked `index: skip` under
a 'Do not read' section, and fails if any internal link is dead. Output is
deterministic (sorted, no timestamps) so re-running is byte-identical.

Usage:
    python build_index.py [corpus_dir]           # write corpus_dir/INDEX.md
    python build_index.py [corpus_dir] --check    # fail (exit 3) if INDEX.md is stale
    python build_index.py --selftest              # prove idempotency + dead-link catch
"""
import os
import re
import sys
import tempfile

START = "<!-- MAP:AUTO START -->"
END = "<!-- MAP:AUTO END -->"
_LINK = re.compile(r"\]\(([^)]+\.md)(?:#[^)]*)?\)")


def parse_frontmatter(text):
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip()] = value.strip()
    return meta


def _md_files(corpus_dir):
    found = []
    for root, _dirs, files in os.walk(corpus_dir):
        for name in sorted(files):
            if name.endswith(".md") and name != "INDEX.md":
                rel = os.path.relpath(os.path.join(root, name), corpus_dir)
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def build(corpus_dir):
    """Return (index_text, dead_links)."""
    entries, traps, dead = [], [], []
    for rel in _md_files(corpus_dir):
        path = os.path.join(corpus_dir, rel)
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        meta = parse_frontmatter(text)
        if meta.get("index") == "skip":
            traps.append(rel)
        else:
            entries.append((rel, meta.get("description", "")))
        base = os.path.dirname(rel)
        for target in _LINK.findall(text):
            if target.startswith(("http://", "https://")):
                continue
            resolved = os.path.normpath(os.path.join(corpus_dir, base, target))
            if not os.path.exists(resolved):
                dead.append(f"{rel} -> {target}")

    lines = ["# Index", "", "Read this map first, then open only the files a task needs.",
             "", START, "", "| Doc | Description |", "| --- | --- |"]
    for rel, desc in entries:
        lines.append(f"| [{rel}]({rel}) | {desc} |")
    if traps:
        lines += ["", "## Do not read (load on demand only)"]
        for rel in sorted(traps):
            lines.append(f"- `{rel}`")
    lines += ["", END, ""]
    return "\n".join(lines), dead


def _write(corpus_dir, text):
    with open(os.path.join(corpus_dir, "INDEX.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _selftest():
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as handle:
        handle.write("---\ndescription: First page.\n---\nSee [b](b.md).\n")
    with open(os.path.join(tmp, "b.md"), "w", encoding="utf-8") as handle:
        handle.write("---\ndescription: Second page.\n---\nBody.\n")
    first, dead1 = build(tmp)
    second, dead2 = build(tmp)
    idempotent = first == second and dead1 == [] and dead2 == []
    with open(os.path.join(tmp, "a.md"), "w", encoding="utf-8") as handle:
        handle.write("---\ndescription: First page.\n---\nSee [gone](missing.md).\n")
    _text, dead3 = build(tmp)
    return idempotent and len(dead3) == 1


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("build_index selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    args = [a for a in argv[1:] if not a.startswith("-")]
    corpus = args[0] if args else "corpus"
    text, dead = build(corpus)
    if dead:
        print("Dead internal links:")
        for item in dead:
            print("  " + item)
        return 2
    if "--check" in argv:
        current = ""
        path = os.path.join(corpus, "INDEX.md")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                current = handle.read()
        if current != text:
            print("INDEX.md is stale. Run: python build_index.py " + corpus)
            return 3
        print("INDEX.md is up to date.")
        return 0
    _write(corpus, text)
    print("Wrote " + os.path.join(corpus, "INDEX.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
