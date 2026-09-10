#!/usr/bin/env python3
"""Coverage guard: tell 'the file exists' apart from 'the file has real content'.

A directory listing says a topic is 'documented'. This guard opens the file and
checks the body is not a stub (too short, or only TODO/TBD/FIXME placeholders),
so an empty page cannot inflate a false sense of completeness.

Usage:
    python guards/check_coverage.py [corpus_dir]
    python guards/check_coverage.py --selftest
"""
import os
import re
import sys

MIN_BODY_CHARS = 40
_PLACEHOLDER_WORDS = {"todo", "tbd", "fixme", "wip", "coming", "soon", "placeholder"}


def strip_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def is_placeholder(body):
    stripped = body.strip()
    if len(re.sub(r"\s", "", stripped)) < MIN_BODY_CHARS:
        return True
    words = set(re.findall(r"[a-zA-Z]+", stripped.lower()))
    return bool(words) and words <= _PLACEHOLDER_WORDS


def run(corpus_dir):
    problems = []
    for root, _dirs, files in os.walk(corpus_dir):
        for name in files:
            if not name.endswith(".md") or name == "INDEX.md":
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as handle:
                body = strip_frontmatter(handle.read())
            if is_placeholder(body):
                problems.append(f"{path}: placeholder or empty content")
    return problems


def _selftest():
    stub = "---\ntitle: X\n---\nTODO\n"
    real = "---\ntitle: X\n---\nThis page explains how to send your first notification with the API.\n"
    return is_placeholder(strip_frontmatter(stub)) and not is_placeholder(strip_frontmatter(real))


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("check_coverage selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    corpus = argv[1] if len(argv) > 1 else "corpus"
    problems = run(corpus)
    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
