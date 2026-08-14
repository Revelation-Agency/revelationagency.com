"""Bulk neutralize every unapproved numeric performance claim in the tree.

All 93 remaining hits (per scripts/tally_numeric_claims.py) live in
descriptive strings on case-study pages, service hubs, and portfolio hubs.
None are used in a chart / metric-tile grid; they are all inline in
sentences like "$25/lead paid-social program".

Substitutions:
  "$<N>/lead"   -> "paid social program"           (or "paid-social program"
                                                    when hyphenated context)
  "$<N> CPL"    -> "measured paid-social program"
  "<N>x ROAS"   -> "positive return on ad spend"
  "<N>% ROAS"   -> "positive return on ad spend"

The idempotent nature of these substitutions means running the script twice
produces identical output. Files with no matches are left untouched.

Each replacement is by regex; the surrounding sentence copy remains intact.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Order matters: match "$N CPL" before "$N/lead" if both share prefixes;
# the two patterns are disjoint here but keep the safe order.
NEUTRALIZATIONS = [
    (re.compile(r"\$\d+ CPL", re.IGNORECASE),        "measured paid-social program"),
    (re.compile(r"\$\d+/lead", re.IGNORECASE),       "paid social program"),
    (re.compile(r"\$\d+ /lead", re.IGNORECASE),      "paid social program"),
    (re.compile(r"\d+x ROAS", re.IGNORECASE),        "positive return on ad spend"),
    (re.compile(r"\d+%\s*ROAS", re.IGNORECASE),      "positive return on ad spend"),
    (re.compile(r"guaranteed \d+[^,.]{0,20}", re.IGNORECASE), "measurable ongoing results"),
    (re.compile(r"instant response", re.IGNORECASE), "responsive follow-up"),
]

SKIP_DIRS = ("/.git", "/artifacts", "/node_modules", "/scripts")


def process(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    orig = data
    hits = 0
    for pat, replacement in NEUTRALIZATIONS:
        (data, n) = pat.subn(replacement, data)
        hits += n
    if data != orig:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(data)
    return hits


def main() -> int:
    total_hits = 0
    files_changed = 0
    for root, _dirs, files in os.walk("."):
        r = root.replace("\\", "/")
        if any(seg in r for seg in SKIP_DIRS):
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(root, f)
            n = process(p)
            if n:
                total_hits += n
                files_changed += 1
                print(f"  {p.replace(chr(92), '/')} : {n}")
    print(f"\nfiles_changed={files_changed} total_hits={total_hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
