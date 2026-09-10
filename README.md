# ai-docs-guardrails

![guards](https://github.com/tuansylee/ai-docs-guardrails/actions/workflows/ci.yml/badge.svg)

This repo is the guardrail system I use to keep an AI-written knowledge base
honest: a small set of deterministic checks that run after every AI agent turn,
and each one ships with a self-test that proves it actually catches a planted
error. The docs in `corpus/` are indexed and checked by the same scripts, so this
repository is also its own demo.

## What each guard does

- `guards/check_numbers.py` reads Markdown tables and fails when a `Total` row
  does not equal the sum of its column.
- `guards/check_checksum.py` validates reference IDs against an IBAN-style mod-97
  check digit, so a mistyped or invented ID is caught.
- `guards/check_crossfile.py` flags a stale value drifting across files, and a
  required fact going missing from the file that owns it.
- `guards/check_coverage.py` tells "the file exists" apart from "the file has real
  content", so an empty stub cannot look finished.
- `guards/style_lint.py` fails the build on em or en dashes and a short list of
  filler words. It is the same writing rule I apply to my own documents.
- `guards/privacy_guard.py` is a hook example that blocks data-exfiltration
  commands (`curl`, `git push`) at command position, and fails open on any error.

Every guard is a single standalone file with no third-party dependencies, so you
can copy one into any project. Each guard has a `--selftest` that plants a
known-bad value and asserts the guard catches it, so the checks are themselves
checked.

## The index

`build_index.py` writes an llms.txt-style map of the docs to `corpus/INDEX.md`:
one row per file harvested from frontmatter, a "do not read" list for
machine-generated files, and a dead-link check. The output is sorted with no
timestamps, so re-running is byte-identical and safe to commit. The idea is
simple: an agent reads the map first and opens only the files a task needs,
instead of crawling the whole tree.

## Try it

    python run_guards.py corpus                 # all guards, silent unless a problem
    for g in guards/*.py; do python "$g" --selftest; done
    python build_index.py corpus --check        # index current and links resolve

Plant a bug and watch it fail:

    # change the Total in corpus/api-reference.md from 175 to a wrong number
    python run_guards.py corpus                 # exits 1 and prints the mismatch

Continuous integration runs the self-tests, the guards on the corpus, and the
index check on every push. The badge above links to the real runs.

## More of my work

Built by Sy Tuan Le, technical writer in Vienna.

- Products in daily use for restaurants and salons in Vienna: https://tuan.at
- First-author paper on SAR land-subsidence monitoring, Remote Sensing 8(4), 2016:
  https://doi.org/10.3390/rs8040338

MIT licensed. See `LICENSE`.
