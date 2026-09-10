#!/usr/bin/env python3
"""Catch a 'Total' row in a Markdown table that does not equal the sum of its column.

An AI draft will happily write a total that no longer matches the numbers above it.
This guard does the arithmetic the model skipped.

Usage:
    python guards/check_numbers.py [corpus_dir]
    python guards/check_numbers.py --selftest
"""
import os
import re
import sys

_SEP = re.compile(r"^:?-+:?$")
_NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _as_number(cell):
    cell = cell.replace(",", "")
    return float(cell) if _NUM.match(cell) else None


def check_text(text):
    """Return a list of problem strings for every mismatching Total row."""
    problems = []
    block = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append(line)
            continue
        if block:
            problems.extend(_check_block(block))
            block = []
    return problems


def _check_block(rows):
    parsed = [_cells(r) for r in rows]
    parsed = [r for r in parsed if not all(_SEP.match(c or "-") for c in r)]  # drop |---|---|
    if len(parsed) < 2:
        return []
    width = max(len(r) for r in parsed)
    total_row = next((r for r in parsed if r and r[0].lower() == "total"), None)
    if total_row is None:
        return []
    data_rows = [r for r in parsed[1:] if r is not total_row and r and r[0].lower() != "total"]
    problems = []
    for col in range(1, width):
        stated = _as_number(total_row[col]) if col < len(total_row) else None
        if stated is None:
            continue
        summed = sum(
            _as_number(r[col]) for r in data_rows
            if col < len(r) and _as_number(r[col]) is not None
        )
        if abs(summed - stated) > 1e-9:
            problems.append(f"Total column {col}: stated {stated:g}, sum of rows is {summed:g}")
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
    good = "| Endpoint | Calls |\n|---|---|\n| a | 120 |\n| b | 40 |\n| Total | 160 |\n"
    bad = "| Endpoint | Calls |\n|---|---|\n| a | 120 |\n| b | 40 |\n| Total | 999 |\n"
    return check_text(good) == [] and len(check_text(bad)) == 1


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("check_numbers selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    corpus = argv[1] if len(argv) > 1 else "corpus"
    problems = run(corpus)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
