#!/usr/bin/env python3

import sys
from pathlib import Path


FORBIDDEN_PATH_PARTS = [
    ".logs/",
    "Library/",
    "Temp/",
    "Obj/",
    "Build/",
    "Builds/",
    "Logs/",
    "UserSettings/",
    "node_modules/",
    "dist/",
    "coverage/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "__pycache__/",
]


FORBIDDEN_SUFFIXES = [
    ".pyc",
    ".pyo",
    ".tmp",
    ".temp",
    ".bak",
    ".swp",
]


ALLOWED_FILES = [
    ".logs/.gitkeep",
]


def is_forbidden(path):
    normalized = path.as_posix()

    if normalized in ALLOWED_FILES:
        return False

    for part in FORBIDDEN_PATH_PARTS:
        if part in normalized:
            return True

    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True

    return False


def main():
    failures = []

    for raw in sys.argv[1:]:
        path = Path(raw)

        if is_forbidden(path):
            failures.append(path.as_posix())

    if failures:
        print("[FAIL] Generated/cache artifacts should not be committed:")
        for failure in failures:
            print("  - %s" % failure)

        print("")
        print("Add these paths to .gitignore or remove them from the commit.")
        return 1

    print("[PASS] No generated/cache artifacts detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
