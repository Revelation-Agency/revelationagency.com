"""Regenerate sitemap.xml from current set of .html pages.

Excludes any page that carries <meta name="robots" content="...noindex...">.
Run from repo root: python scripts/regen_sitemap.py
"""
import os, re
from datetime import datetime

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

EXCLUDE_FILENAMES = {'404.html'}


def meta_for(p):
    if p in ('index.html', ''):
        return ('1.0', 'weekly')
    if p in ('about.html', 'services.html', 'portfolio.html', 'contact.html', 'faq.html', 'booking.html'):
        return ('0.9', 'monthly')
    if p.startswith('the-reveal/'):
        return ('0.7', 'monthly')
    if p.startswith('portfolio/case-studies/'):
        return ('0.7', 'monthly')
    if p.startswith('portfolio/'):
        return ('0.8', 'monthly')
    if p.startswith('services/'):
        return ('0.8', 'monthly')
    return ('0.6', 'monthly')


pages = []
for root, _, files in os.walk(ROOT):
    if any(skip in root for skip in ('node_modules', '.git', '.vercel', '__pycache__', 'scripts')):
        continue
    for f in files:
        if not f.endswith('.html'):
            continue
        rel = os.path.relpath(os.path.join(root, f), ROOT).replace('\\', '/')
        if rel in EXCLUDE_FILENAMES:
            continue
        with open(os.path.join(root, f), 'r', encoding='utf-8') as fp:
            head = fp.read(4000)
        if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', head, re.IGNORECASE):
            continue
        pages.append(rel)

pages.sort()
today = datetime.now().strftime('%Y-%m-%d')

out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
       '']

sections = [
    ('Core pages',            lambda p: '/' not in p),
    ('Services',              lambda p: p.startswith('services/') or p == 'services.html'),
    ('Portfolio',             lambda p: p.startswith('portfolio/')),
    ('The Reveal (articles)', lambda p: p.startswith('the-reveal/')),
    ('Misc',                  lambda _: True),
]

emitted = set()
for sect_name, pred in sections:
    section_pages = [p for p in pages if p not in emitted and pred(p)]
    if not section_pages:
        continue
    out.append(f'  <!-- {sect_name} -->')
    for p in section_pages:
        emitted.add(p)
        priority, freq = meta_for(p)
        loc_path = p
        if loc_path == 'index.html':
            loc_path = ''
        elif loc_path.endswith('/index.html'):
            loc_path = loc_path[:-10]
        out.append('  <url>')
        out.append(f'    <loc>https://revelationagency.com/{loc_path}</loc>')
        out.append(f'    <lastmod>{today}</lastmod>')
        out.append(f'    <changefreq>{freq}</changefreq>')
        out.append(f'    <priority>{priority}</priority>')
        out.append('  </url>')
    out.append('')

out.append('</urlset>')
out.append('')

with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f'Wrote sitemap.xml: {len(pages)} URLs')
