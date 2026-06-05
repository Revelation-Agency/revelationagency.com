"""
Build script for the agent landing pages.

Reads the-reveal/index.html as the boilerplate template (correct depth
prefixes for a 1-level subdirectory page — same depth as lead-agent/
and sales-agent/), then:
  - Swaps <head> meta (title, description, canonical, OG)
  - Replaces the page body between </nav> and the canonical footer marker
    with the landing-page content rendered from PAGE_CONFIGS
  - Injects landing-tracker scripts just before </body>

Niche templating
================
Each agent entry in PAGE_CONFIGS has a 'niches' dict. Each niche entry
overrides the swap points called out in the Notion source-of-truth:
  - 'hero_h1'                : H1 line
  - 'hero_subhead'           : subhead
  - 'opener_body'            : "The difference" / "The problem" paragraph
  - 'step_1_body'            : how-it-works step 1 example (lead-agent only;
                               for sales-agent the niche-specific bits live
                               in 'opener_body')
  - 'built_for_body'         : "Built for ..." paragraph (lead-agent only)
  - 'niche_proof_html'       : optional HTML block above the final CTA

Re-run the script. The base page (no niche) is always written; a niche
page is only written if its override dict is non-empty.

Currently no niche entries are populated — fill in per-niche copy from
Blaine or the Notion docs before re-running for those routes.
"""
from __future__ import annotations
import html
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REPO = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = REPO / 'the-reveal' / 'index.html'

# ---------------------------------------------------------------------------
# Landing-page content (copy is the verbatim Notion source-of-truth)
# ---------------------------------------------------------------------------

PAGE_CONFIGS = {
    'lead-agent': {
        'title_full': 'Revelation Lead Agent System — Revelation Agency',
        'description': (
            'The Revelation Lead Agent System finds the people actually ready '
            'to buy, reaches each one personally, and follows up until they '
            'respond, so your calendar fills with real opportunities instead '
            'of busywork.'
        ),
        'og_image': 'https://revelationagency.com/assets/revelation-logo.png',
        'eyebrow': 'Revelation Lead Agent System',
        'hero_h1': 'The right customers, reached before your competitors know they exist.',
        'hero_subhead': (
            "Most lead generation blasts the same ad to everyone and hands you a "
            "list of tire-kickers. The Revelation Lead Agent System finds the "
            "people actually ready to buy, reaches each one personally, and "
            "follows up until they respond, so your calendar fills with real "
            "opportunities instead of busywork."
        ),
        'cta_primary_label': 'See it for your business',
        'cta_sub': 'No switching software. No long contract to find out if it works.',
        'opener_title': 'The difference',
        'opener_body': (
            "Every other agency runs the same handful of ads across ten businesses "
            "and calls it lead generation. We don't. Every message we send is built "
            "for one specific person, which is exactly why they get answered."
        ),
        'steps_title': 'How it works',
        'steps': [
            {
                'title': 'We find the ready ones.',
                'body': (
                    "Our system watches for the signals that someone has just "
                    "entered a buying moment, so we reach them while the need is "
                    "fresh instead of months too late."
                ),
            },
            {
                'title': 'We do the homework.',
                'body': (
                    "Before a word goes out, each prospect is researched, so the "
                    "outreach speaks to their actual situation."
                ),
            },
            {
                'title': 'We reach the real decision-maker.',
                'body': "Not a generic inbox. The person who can say yes.",
            },
            {
                'title': 'Every message is written for them.',
                'body': (
                    "Custom to their business, their moment, and what they care "
                    "about. Never a template."
                ),
            },
            {
                'title': 'Sent at the right time, followed up on its own.',
                'body': (
                    "Timed for when they're most likely to respond, and followed "
                    "up automatically until you get an answer. Nothing slips."
                ),
            },
        ],
        'get_title': 'What you get',
        'get_items': [
            "A steady flow of the right leads, not a pile of bad ones.",
            "Higher response, because every message is actually relevant.",
            "Zero manual chasing. The system does the follow-up.",
            "A full view of every lead and every touch.",
        ],
        'see_title': 'You see everything',
        'see_body': (
            "Most agencies leave you guessing where your money went. With us "
            "you log in and see every lead, every message, and every result "
            "in real time. No black box."
        ),
        'built_title': 'Built for your business',
        'built_for_body': (
            "The system is tuned to your industry and your market — to how "
            "your customers actually decide and where they actually are."
        ),
        'final_title': 'Want to see what this looks like for your business?',
        'final_body': "Book a 15-minute look.",
        'final_cta_label': 'Book a 15-Minute Look',
        'niches': {
            # Populate per-niche overrides here. Each key under 'niches' is the
            # URL slug (e.g. 'lawyers' → /lead-agent/lawyers). Fields override
            # the base config above. Currently empty — awaiting Blaine's
            # per-niche copy.
            # Example shape (commented):
            # 'lawyers': {
            #     'hero_h1': '...',
            #     'hero_subhead': '...',
            #     'steps_step1_body_override': '...',
            #     'built_for_body': '...',
            # },
        },
    },
    'sales-agent': {
        'title_full': 'Revelation Sales Agent System — Revelation Agency',
        'description': (
            "Leads don't die because they weren't interested. They die in the "
            "follow-up gap. The Revelation Sales Agent System works every lead "
            "the way your best rep would if they had unlimited time, and never "
            "forgets one."
        ),
        'og_image': 'https://revelationagency.com/assets/revelation-logo.png',
        'eyebrow': 'Revelation Sales Agent System',
        'hero_h1': 'Never let another ready-to-buy customer slip through the cracks.',
        'hero_subhead': (
            "Leads don't die because they weren't interested. They die in the "
            "follow-up gap, the callback nobody made, the quote that sat in an "
            "inbox. The Revelation Sales Agent System works every lead the way "
            "your best rep would if they had unlimited time, and never forgets one."
        ),
        'cta_primary_label': 'See it for your business',
        'cta_sub': 'Plugs into what you already use. No switching, no retraining.',
        'opener_title': 'The problem',
        'opener_body': (
            "Your team is busy. Someone says call me next week, someone's "
            "waiting to hear from their spouse, someone's comparing quotes, "
            "and by the time anyone circles back they've gone cold or gone "
            "elsewhere."
        ),
        'steps_title': 'How it works',
        'steps': [
            {
                'title': 'Works every lead like your best rep,',
                'body': "with unlimited time and a perfect memory.",
            },
            {
                'title': 'Remembers what each customer actually said,',
                'body': "the objection, the timing, the detail that matters.",
            },
            {
                'title': 'Follows up at exactly the right moment,',
                'body': (
                    "with a message built around their situation, not a generic blast."
                ),
            },
            {
                'title': 'Sends it itself, or hands your rep the reminder,',
                'body': "with the full context already prepared.",
            },
            {
                'title': 'Plugs into what you already use,',
                'body': "no switching software, no retraining your team.",
            },
            {
                'title': 'Gives managers a clear view,',
                'body': (
                    "which leads are being worked, which objections keep coming "
                    "up, where each rep needs help."
                ),
            },
        ],
        'get_title': 'What you get',
        'get_items': [
            "No quote dies in an inbox. No callback gets forgotten.",
            "More of the leads you already have turn into booked revenue.",
            "A sharper team, without adding a single person.",
        ],
        'see_title': 'You see everything',
        'see_body': (
            "Every conversation, every follow-up, every outcome, visible in "
            "one place in real time. You finally know exactly where every "
            "opportunity stands."
        ),
        'built_title': 'It makes what you have simpler',
        'built_for_body': (
            "It works inside your current setup and actually makes it easier — "
            "your team just works while the assistant handles the remembering "
            "and the follow-through."
        ),
        'final_title': 'See what it would do for your pipeline.',
        'final_body': "Book a 15-minute look.",
        'final_cta_label': 'Book a 15-Minute Look',
        'niches': {
            # Populate per-niche overrides here. Currently empty — awaiting
            # per-niche copy from Notion / Blaine.
        },
    },
}

BOOKING_URL = '../booking'

# ---------------------------------------------------------------------------
# Landing-page CSS — scoped under .la- prefix so it cannot collide with any
# existing site CSS. Added as a single <style> block injected just before
# </head>.
# ---------------------------------------------------------------------------

LANDING_CSS = '''
<style>
/* RA-LANDING-AGENT-CSS-START */
.la-page { font-family: Inter, system-ui, -apple-system, sans-serif; color: var(--charcoal, #2B2B2B); }
.la-container { width: 100%; max-width: 1080px; margin: 0 auto; padding: 0 24px; box-sizing: border-box; }
.la-eyebrow { font-family: Inter, system-ui, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--red, #D72532); display: inline-block; margin-bottom: 18px; }

.la-hero { background: #1E1E1E; color: #fff; padding: clamp(72px, 11vw, 140px) 0 clamp(72px, 11vw, 140px); position: relative; overflow: hidden; }
.la-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 25% 30%, rgba(215,37,50,0.18), transparent 55%); pointer-events: none; }
.la-hero > .la-container { position: relative; }
.la-hero .la-eyebrow { color: #ff5a66; }
.la-h1 { font-family: Orbitron, Inter, system-ui, sans-serif; font-weight: 800; font-size: clamp(2rem, 5.4vw, 3.6rem); line-height: 1.08; letter-spacing: -0.01em; color: #fff; margin: 0 0 24px; max-width: 22ch; }
.la-subhead { font-size: clamp(1rem, 1.4vw, 1.18rem); line-height: 1.55; color: rgba(255,255,255,0.85); max-width: 60ch; margin: 0 0 36px; }
.la-cta-primary { display: inline-flex; align-items: center; gap: 12px; background: var(--red, #D72532); color: #fff !important; text-decoration: none; font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: 15px; letter-spacing: 0.04em; padding: 18px 32px; border-radius: 999px; box-shadow: 0 10px 26px rgba(215,37,50,0.32); transition: transform 0.2s, box-shadow 0.2s, background 0.2s; }
.la-cta-primary:hover { background: #AD1C24; transform: translateY(-2px); box-shadow: 0 14px 32px rgba(215,37,50,0.4); }
.la-cta-primary .la-cta-arrow { font-weight: 900; transition: transform 0.2s; }
.la-cta-primary:hover .la-cta-arrow { transform: translateX(4px); }
.la-cta-sub { font-size: 13px; color: rgba(255,255,255,0.55); margin: 18px 0 0; }

.la-section { padding: clamp(64px, 9vw, 112px) 0; }
.la-section--light { background: #F7F7F5; color: #2B2B2B; }
.la-section--dark { background: #1E1E1E; color: #fff; }
.la-section--dark .la-h2 { color: #fff; }
.la-section--dark .la-body { color: rgba(255,255,255,0.85); }
.la-section--dark .la-eyebrow { color: #ff5a66; }
.la-h2 { font-family: Orbitron, Inter, system-ui, sans-serif; font-weight: 800; font-size: clamp(1.6rem, 3.6vw, 2.4rem); line-height: 1.12; letter-spacing: -0.005em; margin: 0 0 24px; max-width: 22ch; }
.la-body { font-size: clamp(1rem, 1.3vw, 1.12rem); line-height: 1.6; max-width: 62ch; margin: 0; color: #2B2B2B; }

.la-steps { list-style: none; margin: 0; padding: 0; display: grid; gap: 28px; max-width: 760px; }
.la-step { display: grid; grid-template-columns: auto 1fr; gap: 20px; align-items: start; }
.la-step__num { font-family: Orbitron, sans-serif; font-weight: 800; font-size: 18px; color: var(--red, #D72532); background: rgba(215,37,50,0.10); border-radius: 999px; padding: 8px 14px; min-width: 48px; text-align: center; line-height: 1; align-self: start; }
.la-section--dark .la-step__num { background: rgba(215,37,50,0.18); color: #ff8a93; }
.la-step__title { font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: clamp(1.05rem, 1.5vw, 1.22rem); line-height: 1.4; margin: 6px 0 6px; color: inherit; }
.la-step__body { font-size: clamp(0.95rem, 1.2vw, 1.05rem); line-height: 1.6; margin: 0; color: inherit; opacity: 0.85; }

.la-checks { list-style: none; margin: 0; padding: 0; display: grid; gap: 16px; max-width: 720px; }
.la-checks li { display: grid; grid-template-columns: auto 1fr; gap: 14px; font-size: clamp(1rem, 1.3vw, 1.1rem); line-height: 1.55; }
.la-checks li::before { content: ''; display: block; width: 22px; height: 22px; border-radius: 50%; background: var(--red, #D72532); margin-top: 3px; flex-shrink: 0; position: relative; }
.la-checks li { position: relative; }
.la-checks li::after { content: ''; position: absolute; left: 6px; top: 9px; width: 10px; height: 5px; border-left: 2px solid #fff; border-bottom: 2px solid #fff; transform: rotate(-45deg); }

.la-video-slot { background: rgba(0,0,0,0.05); border: 2px dashed rgba(0,0,0,0.18); border-radius: 18px; aspect-ratio: 16 / 9; display: flex; align-items: center; justify-content: center; padding: 24px; max-width: 960px; margin: 0 auto; }
.la-section--dark .la-video-slot { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.18); }
.la-video-slot__placeholder { font-family: Inter, system-ui, sans-serif; font-size: 14px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(0,0,0,0.55); margin: 0; text-align: center; }
.la-section--dark .la-video-slot__placeholder { color: rgba(255,255,255,0.55); }

.la-section--final { background: linear-gradient(135deg, #D72532 0%, #AD1C24 100%); color: #fff; text-align: center; }
.la-section--final .la-h2 { color: #fff; max-width: none; margin-left: auto; margin-right: auto; }
.la-section--final .la-body { color: rgba(255,255,255,0.92); margin-left: auto; margin-right: auto; }
.la-section--final .la-cta-primary { background: #fff; color: var(--red, #D72532) !important; box-shadow: 0 10px 26px rgba(0,0,0,0.18); margin-top: 28px; }
.la-section--final .la-cta-primary:hover { background: #fff; transform: translateY(-2px); box-shadow: 0 14px 32px rgba(0,0,0,0.26); }

@media (max-width: 640px) {
  .la-h1 { font-size: clamp(2rem, 9vw, 2.4rem); }
  .la-h2 { font-size: clamp(1.4rem, 7vw, 1.7rem); }
  .la-step { grid-template-columns: 1fr; gap: 8px; }
  .la-step__num { justify-self: start; min-width: auto; padding: 6px 12px; }
}
/* RA-LANDING-AGENT-CSS-END */
</style>
'''.strip()

TRACKER_SCRIPTS = '''
<!-- RA-LANDING-TRACKER-START -->
<script src="../assets/js/landing-config.js"></script>
<script src="../assets/js/landing-tracker.js"></script>
<!-- RA-LANDING-TRACKER-END -->
'''.strip()

# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_steps(steps):
    out = []
    for i, step in enumerate(steps, 1):
        out.append(
            f'      <li class="la-step">\n'
            f'        <span class="la-step__num">{i:02d}</span>\n'
            f'        <div>\n'
            f'          <h3 class="la-step__title">{esc(step["title"])}</h3>\n'
            f'          <p class="la-step__body">{esc(step["body"])}</p>\n'
            f'        </div>\n'
            f'      </li>'
        )
    return '\n'.join(out)


def render_get_items(items):
    return '\n'.join(f'      <li>{esc(it)}</li>' for it in items)


def render_body(agent_id: str, cfg: dict) -> str:
    return f'''
<main class="la-page">

  <!-- ==================== HERO ==================== -->
  <section class="la-hero">
    <div class="la-container">
      <span class="la-eyebrow">{esc(cfg["eyebrow"])}</span>
      <h1 class="la-h1">{esc(cfg["hero_h1"])}</h1>
      <p class="la-subhead">{esc(cfg["hero_subhead"])}</p>
      <a class="la-cta-primary landing-cta" data-cta="hero" data-page="{esc(agent_id)}" href="{BOOKING_URL}">
        {esc(cfg["cta_primary_label"])} <span class="la-cta-arrow">→</span>
      </a>
      <p class="la-cta-sub">{esc(cfg["cta_sub"])}</p>
    </div>
  </section>

  <!-- ==================== OPENER (Difference / Problem) ==================== -->
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["opener_title"])}</h2>
      <p class="la-body">{esc(cfg["opener_body"])}</p>
    </div>
  </section>

  <!-- ==================== HOW IT WORKS ==================== -->
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["steps_title"])}</h2>
      <ol class="la-steps">
{render_steps(cfg["steps"])}
      </ol>
    </div>
  </section>

  <!-- ==================== WHAT YOU GET ==================== -->
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["get_title"])}</h2>
      <ul class="la-checks">
{render_get_items(cfg["get_items"])}
      </ul>
    </div>
  </section>

  <!-- ==================== YOU SEE EVERYTHING ==================== -->
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["see_title"])}</h2>
      <p class="la-body">{esc(cfg["see_body"])}</p>
    </div>
  </section>

  <!-- ==================== BUILT FOR / SIMPLER ==================== -->
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["built_title"])}</h2>
      <p class="la-body">{esc(cfg["built_for_body"])}</p>
    </div>
  </section>

  <!-- ==================== DEMO VIDEO SLOT ==================== -->
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2">See it in action</h2>
      <div class="la-video-slot" data-video-slot="{esc(agent_id)}-demo">
        <p class="la-video-slot__placeholder">DEMO VIDEO — RESERVED SLOT · EMBED COMING NEXT WEEK</p>
        <!-- TODO(Blaine): replace .la-video-slot innerHTML with the embed
             when the demo video lands. Recommend <iframe> or <video> with
             16:9 aspect — slot already enforces aspect-ratio. -->
      </div>
    </div>
  </section>

  <!-- ==================== FINAL CTA ==================== -->
  <section class="la-section la-section--final">
    <div class="la-container">
      <h2 class="la-h2">{esc(cfg["final_title"])}</h2>
      <p class="la-body">{esc(cfg["final_body"])}</p>
      <a class="la-cta-primary landing-cta" data-cta="footer" data-page="{esc(agent_id)}" href="{BOOKING_URL}">
        {esc(cfg["final_cta_label"])} <span class="la-cta-arrow">→</span>
      </a>
    </div>
  </section>

</main>
'''.strip()


def replace_head_meta(template: str, cfg: dict, canonical_url: str) -> str:
    """Swap title + meta description + canonical + OG meta in the template head."""
    # Title
    template = re.sub(r'<title>.*?</title>',
                       f'<title>{esc(cfg["title_full"])}</title>',
                       template, count=1, flags=re.DOTALL)
    # Meta description
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{esc(cfg["description"])}">',
        template, count=1,
    )
    # Canonical
    template = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical_url}">',
        template, count=1,
    )
    # OG title
    template = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{esc(cfg["title_full"])}">',
        template, count=1,
    )
    # OG description
    template = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{esc(cfg["description"])}">',
        template, count=1,
    )
    # OG URL
    template = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical_url}">',
        template, count=1,
    )
    # OG image
    template = re.sub(
        r'<meta property="og:image" content="[^"]*">',
        f'<meta property="og:image" content="{cfg["og_image"]}">',
        template, count=1,
    )
    return template


NAV_CLOSE = '</nav>'
FOOTER_OPEN = '<!-- RA-FOOTER-CANONICAL-START -->'
BODY_CLOSE = '</body>'
HEAD_CLOSE = '</head>'


def render_page(agent_id: str, cfg: dict, niche_id: str | None = None) -> str:
    """Render a full HTML page (base or niche variant)."""
    template = TEMPLATE_PATH.read_text(encoding='utf-8')

    # Canonical URL
    if niche_id:
        canonical = f'https://revelationagency.com/{agent_id}/{niche_id}'
    else:
        canonical = f'https://revelationagency.com/{agent_id}'

    # 1) Head meta swap
    template = replace_head_meta(template, cfg, canonical)

    # 2) Inject landing CSS just before </head>
    head_pos = template.find(HEAD_CLOSE)
    if head_pos < 0:
        raise RuntimeError('No </head> in template')
    template = template[:head_pos] + '\n' + LANDING_CSS + '\n' + template[head_pos:]

    # 3) Replace body content between </nav> and <!-- RA-FOOTER-CANONICAL-START -->
    nav_end = template.find(NAV_CLOSE)
    footer_open = template.find(FOOTER_OPEN)
    if nav_end < 0 or footer_open < 0:
        raise RuntimeError('Could not find nav/footer boundaries in template')
    nav_end += len(NAV_CLOSE)
    body = render_body(agent_id, cfg)
    template = template[:nav_end] + '\n\n' + body + '\n\n' + template[footer_open:]

    # 4) Inject landing tracker scripts just before </body>
    body_close = template.rfind(BODY_CLOSE)
    if body_close < 0:
        raise RuntimeError('No </body> in template')
    template = template[:body_close] + TRACKER_SCRIPTS + '\n' + template[body_close:]

    return template


def main():
    written = []
    for agent_id, cfg in PAGE_CONFIGS.items():
        # Base page
        out_dir = REPO / agent_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'index.html'
        page_html = render_page(agent_id, cfg, niche_id=None)
        out_path.write_text(page_html, encoding='utf-8')
        written.append((str(out_path.relative_to(REPO)), out_path.stat().st_size))

        # Niche variants (only if overrides present)
        for niche_id, overrides in cfg.get('niches', {}).items():
            if not overrides:
                continue
            merged = {**cfg, **overrides}
            niche_path = out_dir / f'{niche_id}.html'
            niche_html = render_page(agent_id, merged, niche_id=niche_id)
            niche_path.write_text(niche_html, encoding='utf-8')
            written.append((str(niche_path.relative_to(REPO)), niche_path.stat().st_size))

    print(f'Wrote {len(written)} page(s):')
    for path, size in written:
        print(f'  {path}  ({size // 1024} KB)')


if __name__ == '__main__':
    main()
