#!/usr/bin/env python3
"""Single-source-of-truth guard.

Two failure modes it prevents across a docs set:
  1. A stale value drifting into a file (an old version number that was never updated).
  2. A critical fact quietly going missing from the file that is supposed to own it.

Edit CANONICAL and STALE for your project. Putting the word 'corrected' on a line
allows a deliberate historical mention of an old value.

Usage:
    python guards/check_crossfile.py [corpus_dir]
    python guards/check_crossfile.py --selftest
"""
import os
import re
import sys

# A fact that MUST still be present in a named file (path relative to the corpus dir).
CANONICAL = {
    "getting-started.md": "Python 3.10",
}
# A pattern that must NOT appear (an outdated version), unless the line says '(corrected)'.
STALE = re.compile(r"\b2\.3\.\d+\b")


def stale_hits(text):
    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if STALE.search(line) and "corrected" not in line.lower():
            hits.append(f"{lineno}: stale version reference (superseded by 2.4.x)")
    return hits


def run(corpus_dir):
    problems = []
    for root, _dirs, files in os.walk(corpus_dir):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            for msg in stale_hits(text):
                problems.append(f"{path}:{msg}")
    for rel, needle in CANONICAL.items():
        path = os.path.join(corpus_dir, rel)
        text = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        if needle not in text:
            problems.append(f"{path}: missing required fact '{needle}'")
    return problems


def _selftest():
    caught = stale_hits("Install version 2.3.1 now")
    allowed = stale_hits("Older builds used 2.3.1 (corrected: use 2.4.0)")
    return len(caught) == 1 and allowed == []


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("check_crossfile selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    corpus = argv[1] if len(argv) > 1 else "corpus"
    problems = run(corpus)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
