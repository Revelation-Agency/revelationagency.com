"""
Idempotent injector for the mobile grid/column fix v1 (Step 2).

Appends an RA-MOBILE-GRID-FIX-START / RA-MOBILE-GRID-FIX-END block immediately
after the RA-MOBILE-NAV-FIX-END marker (or RA-NAV-MEGAMENU-CSS-END if the nav
fix hasn't run yet). Re-running replaces the block between the markers.

Why: multi-column grids site-wide don't collapse cleanly on mobile. The home
page (index.html) has a global rule that catches BEM __grid/__cols/__columns
patterns, but it's only on the home page. Case-study video pages set inline
grid-template-columns:repeat(3,1fr) which beats every media query. Service
hub leaves use inline 2- and 3-col forced grids. This block generalizes the
home-page rule to every shared-nav page and adds a controlled inline-style
override scoped strictly inside @media (max-width: 767px).

Skips files lacking the marker (the self-contained sales-growth-engine and
sales-intelligence decks).
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPEN  = '/* RA-MOBILE-GRID-FIX-START — v1, do not hand-edit */'
CLOSE = '/* RA-MOBILE-GRID-FIX-END */'

# Prefer to anchor after the Step 1 marker if present, else after the nav block.
ANCHOR_PRIMARY   = '/* RA-MOBILE-NAV-FIX-END */'
ANCHOR_FALLBACK  = '/* RA-NAV-MEGAMENU-CSS-END */'

CSS_BLOCK = '''
@media (max-width: 767px) {
  /* Wildcard collapse — every BEM-named grid/cols/columns container becomes
     single-column on mobile. Covers __grid, __cols, __columns site-wide. */
  [class*="__grid"],
  [class*="__cols"],
  [class*="__columns"] {
    grid-template-columns: 1fr !important;
  }

  /* Specific non-BEM grid classes used on portfolio + section layouts. */
  .pf-grid,
  .three-cards,
  .four-cards,
  .six-cards,
  .cross-grid,
  .ask-grid,
  .timeline-grid,
  .timeline-grid--4,
  .ra-work__grid,
  .ra-work__grid--preview,
  .cover-grid {
    grid-template-columns: 1fr !important;
  }

  /* Controlled inline-style override — collapses any element with an inline
     grid-template-columns:* to a single column on mobile. This is the only
     thing that kills the case-study video pages that hard-coded
     repeat(2,1fr) / repeat(3,1fr) in style attributes. */
  [style*="grid-template-columns"] {
    grid-template-columns: 1fr !important;
  }

  /* Children of grids: full-width, no shrink, no overflowing the cell. */
  [class*="__grid"] > *,
  [class*="__cols"] > *,
  [class*="__columns"] > *,
  .pf-grid > *,
  .cross-grid > *,
  .ask-grid > * {
    max-width: 100% !important;
    min-width: 0 !important;
  }

  /* Gallery items that span 2 cols on desktop must reset on mobile. */
  .cs-gallery__item--wide {
    grid-column: auto !important;
    aspect-ratio: 16 / 9 !important;
  }

  /* Card/tile width discipline — anything in a portfolio/grid context that
     was sized rigidly by inline styles still fits the viewport. */
  .pf-card,
  .cs-service-card,
  .cs-cross__card,
  .cs-metric,
  .sub-portfolio__card,
  .cr-portfolio__card,
  .mk-portfolio__card,
  .strat-work__card,
  .ra-problem__card {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
  }

  /* Embedded media (videos, maps) must fit the column they're in. */
  iframe,
  video,
  embed,
  object {
    max-width: 100% !important;
  }

  /* Horizontal overflow guard — last-line defense. If any descendant
     overflows, body still clips so the page doesn't horizontally scroll. */
  html, body {
    overflow-x: hidden !important;
  }
}
'''.strip()

CANONICAL = OPEN + '\n' + CSS_BLOCK + '\n' + CLOSE
PATTERN = re.compile(re.escape(OPEN) + r'.*?' + re.escape(CLOSE), re.DOTALL)


def inject(text):
    if PATTERN.search(text):
        return PATTERN.sub(lambda _m: CANONICAL, text), 'updated'
    for anchor in (ANCHOR_PRIMARY, ANCHOR_FALLBACK):
        pos = text.find(anchor)
        if pos >= 0:
            insert_at = pos + len(anchor)
            return text[:insert_at] + '\n' + CANONICAL + text[insert_at:], 'injected-after-' + anchor[:30]
    return text, 'skip-no-marker'


def main():
    written = 0
    unchanged = 0
    skipped = 0
    skipped_files = []
    for root, dirs, files in os.walk(ROOT):
        parts = root.split(os.sep)
        if any(p in ('.git', 'node_modules', 'scripts', '.vercel') for p in parts):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            full = os.path.join(root, fn)
            with open(full, 'r', encoding='utf-8') as f:
                text = f.read()
            new_text, status = inject(text)
            rel = os.path.relpath(full, ROOT).replace(os.sep, '/')
            if status == 'skip-no-marker':
                skipped += 1
                skipped_files.append(rel)
                continue
            if new_text != text:
                with open(full, 'w', encoding='utf-8') as f:
                    f.write(new_text)
                written += 1
            else:
                unchanged += 1
    print(f'Written: {written}, Unchanged: {unchanged}, Skipped (no marker): {skipped}')
    if skipped_files:
        print('Skipped files:')
        for s in skipped_files:
            print(f'  {s}')


if __name__ == '__main__':
    main()
