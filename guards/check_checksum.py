#!/usr/bin/env python3
"""Validate reference IDs of the form REF-<number>-<cc>.

The two check digits cc must equal <number> mod 97 (an IBAN-style checksum).
This catches a mistyped or hallucinated ID before it ships in a document.

Usage:
    python guards/check_checksum.py [corpus_dir]
    python guards/check_checksum.py --selftest
"""
import os
import re
import sys

_ID = re.compile(r"REF-(\d+)-(\d{2})")


def check_text(text):
    problems = []
    for match in _ID.finditer(text):
        number = int(match.group(1))
        stated = int(match.group(2))
        expected = number % 97
        if stated != expected:
            problems.append(f"{match.group(0)}: bad checksum (expected {expected:02d})")
    return problems


def run(corpus_dir):
    problems = []
    for root, _dirs, files in os.walk(corpus_dir):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                for msg in check_text(handle.read()):
                    problems.append(f"{path}: {msg}")
    return problems


def _selftest():
    valid = f"REF-100024-{100024 % 97:02d}"
    invalid = "REF-100024-99"
    return check_text(valid) == [] and len(check_text(invalid)) == 1


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("check_checksum selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    corpus = argv[1] if len(argv) > 1 else "corpus"
    problems = run(corpus)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
