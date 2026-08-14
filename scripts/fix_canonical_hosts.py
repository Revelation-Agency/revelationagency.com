"""Ensure every self-referencing canonical / og:url uses the www host.

The base SHA advertises "SEO: canonicalize all self-references to www host"
but 111 pages still have `https://revelationagency.com/...` in one or more
canonical positions. This fixer replaces only the host portion, never the
path — so no page moves.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAT = re.compile(r"https://revelationagency\.com")


def process(path: str) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    if not PAT.search(data):
        return False
    new = PAT.sub("https://www.revelationagency.com", data)
    if new != data:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        return True
    return False


def main() -> int:
    n = 0
    for _dir, _dirs, files in os.walk("."):
        if any(seg in _dir.replace("\\", "/") for seg in ("/.git", "/artifacts", "/node_modules", "/scripts")):
            continue
        for f in files:
            if not f.endswith((".html", ".xml", ".txt", ".json")):
                continue
            if process(os.path.join(_dir, f)):
                n += 1
    print(f"canonical www host: rewrote {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
