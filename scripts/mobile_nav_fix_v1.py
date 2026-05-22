"""
Idempotent injector for the mobile nav fix v1.

Appends an RA-MOBILE-NAV-FIX-START / RA-MOBILE-NAV-FIX-END block immediately
after the RA-NAV-MEGAMENU-CSS-END sentinel inside each HTML file's <style>
block. Re-running replaces the block between the markers (so a v2 swap is
non-destructive).

Why: the canonical nav CSS has a desktop rule
    .ra-nav__links .ra-drop--l2 .ra-drop--l3 a { white-space: nowrap !important }
that bleeds into the mobile breakpoint with higher specificity than the
mobile media query's white-space: normal — pushing nested menu items off
the right edge of the viewport. This fix overrides that and a few other
mobile-only nav legibility / tap-target issues, all inside @media
(max-width: 768px) so desktop styling is untouched.

Pages without the marker (sales-growth-engine, sales-intelligence decks)
have their own self-contained layouts and are skipped automatically.
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPEN  = '/* RA-MOBILE-NAV-FIX-START — v1, do not hand-edit */'
CLOSE = '/* RA-MOBILE-NAV-FIX-END */'
MARKER_NAV_END = '/* RA-NAV-MEGAMENU-CSS-END */'

CSS_BLOCK = '''
@media (max-width: 768px) {
  /* L3 link text MUST wrap on mobile — overrides desktop white-space:nowrap rule.
     Without this, items like "Sales Infrastructure" / "Search & AI Rankings"
     push the open menu wider than the viewport. */
  .ra-nav__links .ra-drop--l2 .ra-drop--l3 a,
  .ra-nav__links .ra-drop--l2 .ra-drop--l3 li a {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    line-height: 1.4 !important;
    padding: 11px 10px !important;
    font-size: 14px !important;
    opacity: 1 !important;
    color: var(--charcoal, #2B2B2B) !important;
    min-height: 40px !important;
    display: flex !important;
    align-items: center !important;
  }

  /* L2 mega-menu: stack to single column on mobile, no min-width, no grid. */
  .ra-nav__links .ra-drop--l2 {
    grid-template-columns: 1fr !important;
    min-width: 0 !important;
    max-width: 100% !important;
    padding: 0 0 0 12px !important;
    gap: 0 !important;
  }

  /* Drop desktop column dividers when stacked. */
  .ra-nav__links .ra-drop--l2 > .has-drop-l3 {
    border-left: 0 !important;
    padding: 0 !important;
  }

  /* Category title (Strategy / Creative / Marketing) — keep red caps, tighten
     padding so it reads as the accordion header on mobile. */
  .ra-nav__links .ra-drop--l2 > .has-drop-l3 > a {
    padding: 12px 4px !important;
    font-size: 12px !important;
    margin-bottom: 0 !important;
    border-bottom: 0 !important;
  }

  /* L2 + L3 link opacity = full (the existing mobile rule used 0.75 which
     made the menu look disabled). */
  .ra-nav__links .ra-drop a { opacity: 1 !important; }

  /* Top-level menu rows hit the 44px iOS tap-target minimum. */
  .ra-nav__links > li > a {
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
  }

  /* Width discipline: nothing inside the nav drawer can exceed its container. */
  .ra-nav__links,
  .ra-nav__links li,
  .ra-nav__links .ra-drop,
  .ra-nav__links .ra-drop--l2,
  .ra-nav__links .ra-drop--l3 {
    max-width: 100% !important;
    box-sizing: border-box;
  }

  /* Accordion toggle chevrons stay visible + tappable. */
  .ra-nav__services-toggle,
  .ra-nav__l2-toggle {
    color: var(--charcoal, #2B2B2B) !important;
    opacity: 1 !important;
  }
}
'''.strip()

CANONICAL = OPEN + '\n' + CSS_BLOCK + '\n' + CLOSE
PATTERN = re.compile(re.escape(OPEN) + r'.*?' + re.escape(CLOSE), re.DOTALL)


def inject(text):
    if PATTERN.search(text):
        return PATTERN.sub(lambda _m: CANONICAL, text), 'updated'
    pos = text.find(MARKER_NAV_END)
    if pos < 0:
        return text, 'skip-no-marker'
    insert_at = pos + len(MARKER_NAV_END)
    return text[:insert_at] + '\n' + CANONICAL + text[insert_at:], 'injected'


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
