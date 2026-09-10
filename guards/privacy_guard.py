#!/usr/bin/env python3
"""Agent-hygiene guard: block data-exfiltration commands an AI agent might run.

Meant to sit on a PreToolUse hook. It inspects the command at COMMAND POSITION,
so `echo "curl ..."` or `grep curl file` are allowed while `curl ...` or
`git push` are blocked. It is FAIL-OPEN: any bug in the guard lets the command
through rather than blocking normal work.

Usage:
    python guards/privacy_guard.py --selftest
    echo '<command>' | python guards/privacy_guard.py   # prints ALLOW or BLOCK
"""
import os
import re
import sys

BLOCK = {"curl", "wget", "scp", "rclone", "nc", "telnet", "ftp", "sftp"}
_ASSIGN = re.compile(r"^\w+=")


def is_blocked(command):
    """Return True if the command exfiltrates data. Fail-open on any error."""
    try:
        for segment in re.split(r"\|\||&&|;|\||\n|&", command):
            tokens = segment.strip().split()
            index = 0
            while index < len(tokens) and _ASSIGN.match(tokens[index]):
                index += 1  # skip leading VAR=value assignments
            if index >= len(tokens):
                continue
            name = os.path.basename(tokens[index])
            if name in BLOCK:
                return True
            if name == "git" and index + 1 < len(tokens) and tokens[index + 1] == "push":
                return True
        return False
    except Exception:
        return False


def _selftest():
    cases = {
        "curl http://example.com/steal": True,
        'echo "curl is just text here"': False,
        "grep -r curl .": False,
        "git push origin main": True,
        "TOKEN=abc wget http://x": True,
        "python build_index.py": False,
    }
    return all(is_blocked(cmd) == expected for cmd, expected in cases.items())


def main(argv):
    if "--selftest" in argv:
        ok = _selftest()
        print("privacy_guard selftest: " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    command = sys.stdin.read()
    print("BLOCK" if is_blocked(command) else "ALLOW")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
