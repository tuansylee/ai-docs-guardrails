#!/usr/bin/env python3
"""Run every corpus guard, stay silent unless something is wrong, and enforce a
per-guard time budget so a hung check cannot stall the pipeline.

Usage:
    python run_guards.py [corpus_dir]
"""
import os
import subprocess
import sys

# Guards that scan the docs corpus. privacy_guard.py is a hook example, not a
# corpus scanner, so it is exercised by its own --selftest in CI, not here.
GUARDS = [
    "style_lint.py",
    "check_numbers.py",
    "check_checksum.py",
    "check_crossfile.py",
    "check_coverage.py",
]
PER_GUARD_SECONDS = 30


def main(argv):
    corpus = argv[1] if len(argv) > 1 else "corpus"
    here = os.path.dirname(os.path.abspath(__file__))
    failures = 0
    for guard in GUARDS:
        path = os.path.join(here, "guards", guard)
        try:
            result = subprocess.run(
                [sys.executable, path, corpus],
                capture_output=True, text=True, timeout=PER_GUARD_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failures += 1
            print(f"[TIMEOUT] {guard} exceeded {PER_GUARD_SECONDS}s")
            continue
        if result.returncode != 0:
            failures += 1
            print(f"[FAIL] {guard}")
            if result.stdout.strip():
                print(result.stdout.rstrip())
    if failures:
        print(f"{failures} guard(s) reported problems.")
        return 1
    print(f"OK: {len(GUARDS)} guards passed on '{corpus}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
