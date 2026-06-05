#!/usr/bin/env python3

import re
import sys
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"firebase[_-]?api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"client[_-]?secret\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"access[_-]?token\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"token\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
]


ALLOWLIST_PATH_PARTS = [
    "docs/examples",
    "docs/templates",
    ".env.example",
    "example",
    "sample",
]


BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".psd",
    ".fbx",
    ".blend",
    ".wav",
    ".mp3",
    ".ogg",
    ".mp4",
    ".dll",
    ".so",
    ".dylib",
    ".exe",
    ".zip",
    ".unitypackage",
    ".pdf",
    ".mov",
}


def is_allowlisted(path):
    normalized = path.as_posix().lower()
    return any(part in normalized for part in ALLOWLIST_PATH_PARTS)


def main():
    failures = []

    for raw in sys.argv[1:]:
        path = Path(raw)

        if not path.exists() or path.is_dir():
            continue

        if path.suffix.lower() in BINARY_SUFFIXES:
            continue

        if is_allowlisted(path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    failures.append(
                        "%s:%s: possible secret/private key detected"
                        % (path.as_posix(), line_number)
                    )

    if failures:
        print("[FAIL] Possible secrets detected:")
        for failure in failures:
            print("  - %s" % failure)

        print("")
        print("Move real secrets to local .env, ignored local config, or CI secrets.")
        print("Commit only .env.example / config templates.")
        return 1

    print("[PASS] No obvious secrets detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
