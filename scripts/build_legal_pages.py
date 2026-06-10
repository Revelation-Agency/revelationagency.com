"""
Build /privacy-policy and /terms from the legal markdown source-of-truth
(legal/source.md) and inject footer links to both new pages site-wide.

Source: legal/source.md (full markdown with operator note + bracketed
fields).  Build pass:
  - Strip the italicized "Operator note" block (everything before the
    first horizontal rule).
  - Replace [DATE] with today's date in long form (e.g. "June 10, 2026").
  - Replace [PHONE] / [PHONE — optional] with 559-201-7039.
  - Split on `# Privacy Policy` / `# Terms of Service` and render each
    half into a standalone HTML page using about.html as the boilerplate
    template (correct depth for root-level pages).
  - Inject the Privacy / Terms / Contact link group into the canonical
    footer bottom row across every shared-nav page so the new pages are
    discoverable from anywhere on the site.

Idempotent: rerun any time to update both pages and refresh links.
"""
from __future__ import annotations
import html
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO = Path(__file__).resolve().parents[1]
SOURCE_MD = REPO / 'legal' / 'source.md'
TEMPLATE_PATH = REPO / 'about.html'

PHONE = '559-201-7039'
TODAY = date(2026, 6, 10).strftime('%B %-d, %Y') if os.name != 'nt' else date(2026, 6, 10).strftime('%B %#d, %Y')


# ---------------------------------------------------------------------------
# Tiny markdown → HTML converter (handles what's in our source).
# ---------------------------------------------------------------------------

def md_inline(text: str) -> str:
    """Convert inline markdown (bold, links). Everything else is escaped first."""
    # Use a tokenization pass so we can leave inline markup alone while escaping
    # the surrounding text. We split on the inline markup patterns and rebuild.
    parts = []
    i = 0
    pattern = re.compile(r'\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)')
    for m in pattern.finditer(text):
        if m.start() > i:
            parts.append(html.escape(text[i:m.start()]))
        if m.group(1) is not None:
            parts.append('<strong>' + html.escape(m.group(1)) + '</strong>')
        else:
            label = html.escape(m.group(2))
            href = html.escape(m.group(3), quote=True)
            parts.append(f'<a href="{href}">{label}</a>')
        i = m.end()
    if i < len(text):
        parts.append(html.escape(text[i:]))
    return ''.join(parts)


def md_to_html(md: str) -> str:
    """Convert one policy/terms body markdown into HTML.

    Top-level `# Heading` is dropped — caller renders that in the hero.
    Buffers consecutive non-empty non-list lines into a single paragraph
    with <br>-separated lines (so the address blocks render cleanly).
    """
    lines = md.split('\n')
    out = []
    in_list = False
    para_buf: list[str] = []

    def flush_para():
        nonlocal para_buf
        if para_buf:
            # Each line of the paragraph buffer becomes a `<br>`-separated
            # line in the output paragraph — preserves the address-block
            # layout while keeping it semantically one paragraph.
            inner = '<br>'.join(md_inline(l) for l in para_buf)
            out.append(f'<p class="legal-p">{inner}</p>')
            para_buf = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_para()
            close_list()
            continue
        if stripped.startswith('# '):
            # Drop the top-level H1 — the hero renders the title separately.
            flush_para()
            close_list()
            continue
        if stripped.startswith('## '):
            flush_para()
            close_list()
            out.append(f'<h2 class="legal-h2">{md_inline(stripped[3:])}</h2>')
            continue
        if stripped.startswith('### '):
            flush_para()
            close_list()
            out.append(f'<h3 class="legal-h3">{md_inline(stripped[4:])}</h3>')
            continue
        if stripped == '---':
            flush_para()
            close_list()
            out.append('<hr class="legal-hr">')
            continue
        if stripped.startswith('- '):
            flush_para()
            if not in_list:
                out.append('<ul class="legal-list">')
                in_list = True
            out.append(f'<li>{md_inline(stripped[2:])}</li>')
            continue
        # Regular text line — buffer until paragraph break.
        close_list()
        para_buf.append(stripped)

    flush_para()
    close_list()
    return '\n'.join(out)


# ---------------------------------------------------------------------------
# Pull the privacy + terms bodies out of the source markdown.
# ---------------------------------------------------------------------------

def load_and_split() -> tuple[str, str]:
    raw = SOURCE_MD.read_text(encoding='utf-8')
    # Substitute bracketed fields BEFORE splitting (covers DATE / PHONE in
    # both halves at once).
    raw = raw.replace('[DATE]', TODAY)
    raw = raw.replace('[PHONE — optional]', PHONE)
    raw = raw.replace('[PHONE]', PHONE)

    # The operator note is everything from the top down to (and including)
    # the first `---`. Strip it.
    parts = raw.split('\n---\n')
    if len(parts) < 3:
        raise RuntimeError(
            'Source markdown structure unexpected — need at least 3 ---'
            f'-separated sections, found {len(parts)}'
        )
    # parts[0] = operator note + top H1; parts[1] = privacy policy body
    # (starts with "# Privacy Policy"); parts[2] = terms body (starts
    # with "# Terms of Service").
    privacy_md = parts[1].strip()
    terms_md = parts[2].strip()
    if not privacy_md.lstrip().startswith('# Privacy Policy'):
        raise RuntimeError('Expected privacy section to start with "# Privacy Policy"')
    if not terms_md.lstrip().startswith('# Terms of Service'):
        raise RuntimeError('Expected terms section to start with "# Terms of Service"')
    return privacy_md, terms_md


# ---------------------------------------------------------------------------
# Page renderer — boilerplate from about.html + new head meta + new body.
# ---------------------------------------------------------------------------

LEGAL_CSS = '''
<style>
/* RA-LEGAL-PAGE-CSS-START */
.legal-page { background: #fff; color: var(--charcoal, #2B2B2B); font-family: Inter, system-ui, -apple-system, sans-serif; }
.legal-container { width: 100%; max-width: 820px; margin: 0 auto; padding: 0 24px; box-sizing: border-box; }

.legal-hero { background: #1E1E1E; color: #fff; padding: clamp(80px, 11vw, 140px) 0 clamp(56px, 7vw, 84px); position: relative; overflow: hidden; }
.legal-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 80% 30%, rgba(215,37,50,0.18), transparent 55%); pointer-events: none; }
.legal-hero > .legal-container { position: relative; }
.legal-eyebrow { font-size: 13px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: #ff5a66; display: inline-block; margin: 0 0 18px; }
.legal-h1 { font-family: Orbitron, Inter, sans-serif; font-weight: 800; font-size: clamp(2.1rem, 5vw, 3.2rem); line-height: 1.08; letter-spacing: -0.01em; color: #fff; margin: 0 0 18px; }
.legal-meta { font-size: 15px; line-height: 1.55; color: rgba(255,255,255,0.7); margin: 0; }
.legal-meta strong { color: #fff; font-weight: 600; }

.legal-body { padding: clamp(56px, 8vw, 96px) 0 clamp(80px, 10vw, 120px); background: #fff; }
.legal-body h2.legal-h2 { font-family: Orbitron, Inter, sans-serif; font-weight: 800; font-size: clamp(1.4rem, 2.4vw, 1.7rem); line-height: 1.2; letter-spacing: -0.005em; margin: clamp(40px, 5vw, 56px) 0 18px; color: var(--off-black, #1E1E1E); }
.legal-body h2.legal-h2:first-child { margin-top: 0; }
.legal-body h3.legal-h3 { font-family: Inter, sans-serif; font-weight: 700; font-size: clamp(1.1rem, 1.7vw, 1.22rem); line-height: 1.3; margin: 28px 0 12px; color: var(--off-black, #1E1E1E); }
.legal-body p.legal-p { font-size: 16px; line-height: 1.7; color: rgba(43,43,43,0.92); margin: 0 0 18px; }
.legal-body p.legal-p strong { color: var(--off-black, #1E1E1E); font-weight: 700; }
.legal-body a { color: var(--red, #D72532); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
.legal-body a:hover { color: var(--red-deep, #AD1C24); }

.legal-body ul.legal-list { list-style: none; padding: 0; margin: 0 0 22px; }
.legal-body ul.legal-list li { position: relative; padding: 0 0 0 24px; margin: 0 0 12px; font-size: 16px; line-height: 1.65; color: rgba(43,43,43,0.92); }
.legal-body ul.legal-list li::before { content: ''; position: absolute; left: 4px; top: 11px; width: 8px; height: 8px; border-radius: 50%; background: var(--red, #D72532); }
.legal-body ul.legal-list li strong { color: var(--off-black, #1E1E1E); font-weight: 700; }

.legal-body hr.legal-hr { border: 0; border-top: 1px solid rgba(0,0,0,0.08); margin: clamp(48px, 6vw, 72px) 0; }

@media (max-width: 640px) {
  .legal-h1 { font-size: clamp(1.85rem, 8vw, 2.2rem); }
  .legal-body p.legal-p, .legal-body ul.legal-list li { font-size: 15.5px; }
}
/* RA-LEGAL-PAGE-CSS-END */
</style>
'''.strip()


NAV_CLOSE = '</nav>'
FOOTER_OPEN = '<!-- RA-FOOTER-CANONICAL-START -->'
HEAD_CLOSE = '</head>'


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def replace_head_meta(template: str, title: str, description: str, slug: str) -> str:
    canonical = f'https://revelationagency.com/{slug}'
    template = re.sub(r'<title>.*?</title>',
                       f'<title>{esc(title)}</title>',
                       template, count=1, flags=re.DOTALL)
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{esc(description)}">',
        template, count=1,
    )
    template = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{esc(title)}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{esc(description)}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical}">',
        template, count=1,
    )
    return template


def build_page(title: str, eyebrow: str, header_h1: str, meta_line: str,
               body_html: str, description: str, slug: str) -> str:
    template = TEMPLATE_PATH.read_text(encoding='utf-8')

    # Head meta
    template = replace_head_meta(template, title, description, slug)

    # Inject legal CSS before </head>
    head_pos = template.find(HEAD_CLOSE)
    if head_pos < 0:
        raise RuntimeError('No </head> in template')
    template = template[:head_pos] + '\n' + LEGAL_CSS + '\n' + template[head_pos:]

    # Body content between </nav> and the footer marker
    nav_end = template.find(NAV_CLOSE)
    footer_open = template.find(FOOTER_OPEN)
    if nav_end < 0 or footer_open < 0:
        raise RuntimeError('Could not find nav/footer boundaries in template')
    nav_end += len(NAV_CLOSE)

    body = f'''
<main class="legal-page">
  <section class="legal-hero">
    <div class="legal-container">
      <span class="legal-eyebrow">{esc(eyebrow)}</span>
      <h1 class="legal-h1">{esc(header_h1)}</h1>
      <p class="legal-meta">{meta_line}</p>
    </div>
  </section>
  <section class="legal-body">
    <div class="legal-container">
{body_html}
    </div>
  </section>
</main>
'''.strip()

    template = template[:nav_end] + '\n\n' + body + '\n\n' + template[footer_open:]
    return template


# ---------------------------------------------------------------------------
# Footer link injection — adds Privacy / Terms / Contact links to the
# canonical footer bottom row across every shared-nav page.
# ---------------------------------------------------------------------------

# Pattern matches: <div class="ra-footer__bottom"> ... <p class="ra-footer__copyright">&copy; 2026 <a href="(.*)index.html">Revelation Agency</a>. Dream. Build. Scale.</p> ... </div>
# We replace the entire <div class="ra-footer__bottom"> ... </div> block.

FOOTER_BOTTOM_PATTERN = re.compile(
    r'<div class="ra-footer__bottom">\s*'
    r'<p class="ra-footer__copyright">&copy; 2026 <a href="(?P<prefix>[^"]*?)index\.html">Revelation Agency</a>\. Dream\. Build\. Scale\.</p>'
    # Optional pre-existing legal nav (idempotency — strip it on re-run).
    r'(?:\s*<nav class="ra-footer__legal"[\s\S]*?</nav>)?'
    r'\s*</div>',
)

# The new replacement keeps the original copyright line, adds a small
# legal nav with Privacy / Terms / Contact, and uses the same prefix the
# copyright link uses so paths are correct at any depth.
FOOTER_BOTTOM_TEMPLATE = (
    '<div class="ra-footer__bottom">\n'
    '      <p class="ra-footer__copyright">&copy; 2026 <a href="{prefix}index.html">Revelation Agency</a>. Dream. Build. Scale.</p>\n'
    '      <nav class="ra-footer__legal" aria-label="Legal">\n'
    '        <a href="{prefix}privacy-policy">Privacy Policy</a>\n'
    '        <a href="{prefix}terms">Terms</a>\n'
    '        <a href="{prefix}contact">Contact</a>\n'
    '      </nav>\n'
    '    </div>'
)

# CSS to style the new legal nav row. Injected once into the canonical
# footer CSS block (matched by the .ra-footer__copyright a selector that
# already exists everywhere).
LEGAL_NAV_CSS = (
    '\n.ra-footer__legal { display: flex; flex-wrap: wrap; gap: 18px; align-items: center; }'
    '\n.ra-footer__legal a { font-size: 13px; color: rgba(255,255,255,0.45); text-decoration: none; letter-spacing: 0.02em; }'
    '\n.ra-footer__legal a:hover { color: #fff; }'
    '\n@media (max-width: 640px) { .ra-footer__bottom { flex-direction: column; gap: 12px; align-items: flex-start; } }\n'
)

# Sentinel-wrapped CSS block — idempotent (replace on re-run).
LEGAL_NAV_CSS_OPEN = '/* RA-FOOTER-LEGAL-NAV-CSS-START */'
LEGAL_NAV_CSS_CLOSE = '/* RA-FOOTER-LEGAL-NAV-CSS-END */'
LEGAL_NAV_CSS_BLOCK = LEGAL_NAV_CSS_OPEN + LEGAL_NAV_CSS + LEGAL_NAV_CSS_CLOSE
LEGAL_NAV_CSS_PATTERN = re.compile(
    re.escape(LEGAL_NAV_CSS_OPEN) + r'.*?' + re.escape(LEGAL_NAV_CSS_CLOSE),
    re.DOTALL,
)

# Where to insert the CSS — immediately after the existing footer__copyright
# hover rule so it lives inside the canonical footer CSS region.
COPY_HOVER_ANCHOR = '.ra-footer__copyright a:hover { color: white; }'


def inject_footer_links(html_text: str) -> tuple[str, str]:
    """Add Privacy / Terms / Contact links to .ra-footer__bottom and the
    accompanying CSS. Idempotent — re-running collapses prior insertions
    back to a single block.

    Returns (new_text, status) where status is one of:
      'updated', 'unchanged', 'skip-no-footer'.
    """
    new_text = html_text

    # Replace existing CSS block (if present) so we can swap formatting.
    if LEGAL_NAV_CSS_PATTERN.search(new_text):
        new_text = LEGAL_NAV_CSS_PATTERN.sub(LEGAL_NAV_CSS_BLOCK, new_text)
    else:
        # Insert AFTER the copyright hover rule. There may be multiple
        # copies of this rule in the file (the canonical footer CSS is
        # duplicated across the `<style>` blocks in some templates) — we
        # only need to inject once. count=1 keeps it idempotent.
        if COPY_HOVER_ANCHOR not in new_text:
            return html_text, 'skip-no-footer'
        new_text = new_text.replace(
            COPY_HOVER_ANCHOR,
            COPY_HOVER_ANCHOR + LEGAL_NAV_CSS_BLOCK,
            1,
        )

    # Replace the footer bottom row.
    m = FOOTER_BOTTOM_PATTERN.search(new_text)
    if not m:
        # No matching footer bottom — leave the file alone and report.
        return html_text, 'skip-no-footer'
    prefix = m.group('prefix')
    new_block = FOOTER_BOTTOM_TEMPLATE.format(prefix=prefix)
    new_text = FOOTER_BOTTOM_PATTERN.sub(new_block, new_text, count=1)

    if new_text == html_text:
        return html_text, 'unchanged'
    return new_text, 'updated'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    privacy_md, terms_md = load_and_split()

    privacy_body = md_to_html(privacy_md)
    terms_body = md_to_html(terms_md)

    privacy_html = build_page(
        title='Privacy Policy — Revelation Agency',
        eyebrow='Legal',
        header_h1='Privacy Policy',
        meta_line=f'<strong>Effective date:</strong> {TODAY} &nbsp;·&nbsp; <strong>Last updated:</strong> {TODAY}',
        body_html=privacy_body,
        description='How Revelation Agency collects, uses, shares, and safeguards information from website visitors, prospects, clients, and the platform data we access on behalf of clients.',
        slug='privacy-policy',
    )
    (REPO / 'privacy-policy.html').write_text(privacy_html, encoding='utf-8')
    print(f'WROTE  privacy-policy.html  ({len(privacy_html)//1024} KB)')

    terms_html = build_page(
        title='Terms of Service — Revelation Agency',
        eyebrow='Legal',
        header_h1='Terms of Service',
        meta_line=f'<strong>Effective date:</strong> {TODAY}',
        body_html=terms_body,
        description='Terms governing access to and use of the revelationagency.com website. Services we provide to clients are governed by separate written agreements.',
        slug='terms',
    )
    (REPO / 'terms.html').write_text(terms_html, encoding='utf-8')
    print(f'WROTE  terms.html  ({len(terms_html)//1024} KB)')

    # Sitewide footer link injection.
    written = 0
    unchanged = 0
    skipped = []
    for root, dirs, files in os.walk(REPO):
        parts = root.split(os.sep)
        if any(p in ('.git', 'node_modules', 'scripts', '.vercel', 'legal') for p in parts):
            continue
        for fn in files:
            if not fn.endswith('.html'):
                continue
            full = os.path.join(root, fn)
            with open(full, 'r', encoding='utf-8') as f:
                text = f.read()
            new_text, status = inject_footer_links(text)
            rel = os.path.relpath(full, REPO).replace(os.sep, '/')
            if status == 'skip-no-footer':
                skipped.append(rel)
                continue
            if new_text != text:
                with open(full, 'w', encoding='utf-8') as f:
                    f.write(new_text)
                written += 1
            else:
                unchanged += 1
    print(f'\nFooter link injection: {written} written, {unchanged} unchanged, {len(skipped)} skipped')
    if skipped:
        print('Skipped (no canonical footer match):')
        for s in skipped[:10]:
            print(f'  {s}')
        if len(skipped) > 10:
            print(f'  ...and {len(skipped)-10} more')


if __name__ == '__main__':
    main()
