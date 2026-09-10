#!/usr/bin/env python3
"""Fail the build when docs contain em/en dashes or AI-cliche words.

Standalone by design: copy this single file into any docs project.
Usage:
    python guards/style_lint.py [corpus_dir]   # scan, exit 1 if problems
    python guards/style_lint.py --selftest      # prove it catches a planted error
"""
import os
import re
import sys

# Words that make writing read as machine-generated. Keep this list short and honest.
BANNED = [
    "leverage", "spearhead", "utilize", "seamless", "delve", "showcase",
    "underscore", "robust", "passionate", "results-driven", "decision-ready",
]
DASHES = {"—": "em-dash", "–": "en-dash"}


def lint_text(text):
    """Return a list of 'line: problem' strings. Pure function so it is easy to test."""
    problems = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for ch, name in DASHES.items():
            if ch in line:
                problems.append(f"{lineno}: {name} found (use a comma or split the sentence)")
        low = line.lower()
        for word in BANNED:
            if re.search(r"\b" + re.escape(word) + r"\b", low):
                problems.append(f"{lineno}: banned word '{word}'")
    return problems


def run(corpus_dir):
    problems = []
    for root, _dirs, files in os.walk(corpus_dir):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                for msg in lint_text(handle.read()):
                    problems.append(f"{path}:{msg}")
    return problems


def _selftest():
    bad = "We leverage synergy—right now."
    found = lint_text(bad)
    # Expect at least the em-dash and the banned word 'leverage'.
    return any("em-dash" in p for p in found) and any("leverage" in p for p in found)


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("style_lint selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    corpus = argv[1] if len(argv) > 1 else "corpus"
    problems = run(corpus)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
