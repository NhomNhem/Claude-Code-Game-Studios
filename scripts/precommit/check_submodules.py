#!/usr/bin/env python3

import subprocess
import sys


def run(args):
    result = subprocess.run(
        args,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def main():
    code, output, error = run(["git", "submodule", "status", "--recursive"])

    if code != 0:
        print("[FAIL] Could not read submodule status.")
        if error:
            print(error)
        return 1

    failures = []

    for line in output.splitlines():
        if not line:
            continue

        prefix = line[0]
        parts = line.split()

        if len(parts) < 2:
            continue

        path = parts[1]

        if prefix == "-":
            failures.append("%s: submodule not initialized" % path)
        elif prefix == "+":
            failures.append(
                "%s: submodule working tree is not at committed parent pointer" % path
            )
        elif prefix == "U":
            failures.append("%s: submodule has merge conflict" % path)

        dirty_code, dirty_output, dirty_error = run(
            ["git", "-C", path, "status", "--short"]
        )

        if dirty_code != 0:
            failures.append("%s: could not read git status" % path)
            if dirty_error:
                failures.append("%s: %s" % (path, dirty_error))
            continue

        if dirty_output:
            failures.append("%s: submodule has uncommitted changes" % path)

    if failures:
        print("[FAIL] Submodule hygiene check failed:")
        for failure in failures:
            print("  - %s" % failure)

        print("")
        print("Expected flow:")
        print("  1. Commit inside changed submodule")
        print("  2. Push submodule branch")
        print("  3. Return to parent repo")
        print("  4. Stage submodule pointer in parent")
        print("  5. Commit parent repo")
        return 1

    print("[PASS] Submodule hygiene check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
