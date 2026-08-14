"""One-shot audit: enumerate every unapproved numeric performance claim in
the tree so the neutralizer can be extended."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

NUMERIC_CLAIM_RE = re.compile(
    r"\$\d+/lead|\$\d+ CPL|\d+% (conversion|ROAS|CPL|open|reply)|\d+x ROAS|"
    r"guaranteed \d|instant response",
    re.IGNORECASE,
)

def main() -> int:
    tally = {}
    for root, _dirs, files in os.walk("."):
        r = root.replace("\\", "/")
        if any(seg in r for seg in ("/.git", "/artifacts", "/node_modules")):
            continue
        for f in files:
            if not f.endswith(".html"):
                continue
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8") as fh:
                data = fh.read()
            hits = [m.group(0) for m in NUMERIC_CLAIM_RE.finditer(data)]
            if hits:
                tally[p.replace("\\", "/")] = hits
    for p, hs in sorted(tally.items()):
        print(f"{p} : {len(hs)}")
        for h in hs[:5]:
            print(f"    {h}")
    print(f"\ntotal files={len(tally)}, total hits={sum(len(v) for v in tally.values())}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
