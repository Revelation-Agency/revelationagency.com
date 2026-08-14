import os
import re
from collections import defaultdict

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

d = defaultdict(list)
t = defaultdict(list)
for root, _dirs, files in os.walk("."):
    r = root.replace("\\", "/")
    if any(seg in r for seg in ("/.git", "/artifacts", "/node_modules")):
        continue
    for f in files:
        if not f.endswith(".html"):
            continue
        p = os.path.join(root, f).replace("\\", "/")
        with open(p, "r", encoding="utf-8") as fh:
            data = fh.read()
        m = re.search(r'<meta name="description" content="([^"]+)"', data)
        if m:
            d[m.group(1).strip()].append(p)
        m = re.search(r"<title>([^<]+)</title>", data)
        if m:
            t[m.group(1).strip()].append(p)

print("== duplicate descriptions ==")
for desc, files in d.items():
    if len(files) > 1:
        print(f"[{len(files)}] {desc[:100]}")
        for f in files[:6]:
            print("   ", f)
print("\n== duplicate titles ==")
for title, files in t.items():
    if len(files) > 1:
        print(f"[{len(files)}] {title[:100]}")
        for f in files[:6]:
            print("   ", f)
