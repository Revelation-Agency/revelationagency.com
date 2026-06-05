"""
Build script for /lead-agent and /sales-agent landing pages — POLISH PASS.

Reads the-reveal/index.html as the boilerplate template (correct depth
prefixes for a 1-level subdirectory page), then:
  - Swaps <head> meta (title, description, canonical, OG)
  - Injects the landing-page CSS + page-specific JS hooks
  - Replaces the body between </nav> and the canonical footer marker
    with rich, animated landing content rendered from PAGE_CONFIGS
  - Wires the sticky CTA bar + landing tracker + landing animations

CTA standard (Notion source-of-truth, 2026-06-05):
  Label everywhere = "Book Your Strategy Session Now"
  Destination      = ../booking (Vercel cleanUrls → /booking)
  Sticky bar       = mobile + desktop, slides in after hero leaves viewport
  Repeated         = after every major section, not just hero + footer
  All CTAs carry   = .landing-cta (tracker hook)

Visual polish (per Notion):
  Lead Agent — animated signals → pipeline hero, scroll-revealed steps,
    animated count-up stats with citable benchmarks + comparative chart,
    looping mini-dashboard preview in the "You see everything" section.
  Sales Agent — animated follow-up timeline hero, scroll-revealed steps,
    animated count-ups + comparative chart, interactive before/after
    toggle ("deal slips" / "deal saved"), recurring-objection scorecard
    preview in the "You see everything" section.

Stats honesty: every number is a real, citable industry benchmark
(cited inline beneath the stat) or clearly labeled "illustrative."
No fabricated Revelation client results.

Niche templating: PAGE_CONFIGS['<agent>']['niches']['<slug>'] dict
overrides any field on the base config and produces <agent>/<slug>.html
on re-run. Currently empty — Blaine fills in per-niche copy.
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
# Content config — copy is the verbatim Notion source-of-truth.
# ---------------------------------------------------------------------------

CTA_LABEL = 'Book Your Strategy Session Now'
CTA_HREF = '../booking'

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
        # Stat band — citable industry benchmarks, no fabricated client results.
        'stats_title': 'The math of being on time.',
        'stats': [
            {
                'value': 21,
                'suffix': 'x',
                'label': 'more likely to make contact when you reach a lead within 5 minutes vs. 30 minutes.',
                'source': 'Harvard Business Review, 2011 — Oldroyd / McElheran / Elkington, "The Short Life of Online Sales Leads."',
            },
            {
                'value': 35,
                'suffix': '%',
                'label': 'of sales go to the vendor that responds first.',
                'source': 'InsideSales.com / Velocify Lead Response Survey.',
            },
            {
                'value': 7,
                'suffix': '%',
                'label': 'of companies respond to a new lead within five minutes.',
                'source': 'Drift, State of Conversational Marketing 2018 (433 B2B companies surveyed).',
            },
        ],
        'compare_title': 'Working each lead — without vs. with the system',
        'compare_bars': [
            {
                'label': 'Industry — companies responding within 5 minutes',
                'pct': 7,
                'note': 'Drift, State of Conversational Marketing 2018.',
                'kind': 'against',
            },
            {
                'label': 'Working every lead, on time',
                'pct': 100,
                'note': 'Illustrative — the system\'s design intent.',
                'kind': 'with',
            },
        ],
        'niches': {},
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
        'stats_title': 'Where revenue actually leaks.',
        'stats': [
            {
                'value': 44,
                'suffix': '%',
                'label': 'of sales reps give up after one follow-up.',
                'source': 'Brevet Group / Marketing Donut sales statistics.',
            },
            {
                'value': 80,
                'suffix': '%',
                'label': 'of sales require five or more follow-ups to close.',
                'source': 'Brevet Group / Marketing Donut sales statistics.',
            },
            {
                'value': 21,
                'suffix': 'x',
                'label': 'more likely to make contact when you reach a lead within 5 minutes vs. 30 minutes.',
                'source': 'Harvard Business Review, 2011 — Oldroyd / McElheran / Elkington, "The Short Life of Online Sales Leads."',
            },
        ],
        'compare_title': 'Working every lead — without vs. with the system',
        'compare_bars': [
            {
                'label': 'Reps still following up after attempt 1',
                'pct': 56,
                'note': 'Brevet Group — 44% give up after the first follow-up.',
                'kind': 'against',
            },
            {
                'label': 'Every lead worked, every time',
                'pct': 100,
                'note': 'Illustrative — the system\'s design intent.',
                'kind': 'with',
            },
        ],
        'niches': {},
    },
}


# ---------------------------------------------------------------------------
# CSS — scoped under .la- prefix. Injected before </head>.
# ---------------------------------------------------------------------------

LANDING_CSS = '''
<style>
/* RA-LANDING-AGENT-CSS-START */
:root { --la-red: #D72532; --la-red-deep: #AD1C24; --la-charcoal: #2B2B2B; --la-off-black: #1E1E1E; --la-grey-light: #F7F7F5; --la-grey-mid: #C9C9C5; }

.la-page { font-family: Inter, system-ui, -apple-system, sans-serif; color: var(--la-charcoal); }
.la-container { width: 100%; max-width: 1180px; margin: 0 auto; padding: 0 24px; box-sizing: border-box; }
.la-eyebrow { font-family: Inter, system-ui, sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--la-red); display: inline-block; margin: 0 0 18px; }

/* ---------------- Reveals ---------------- */
.la-reveal { opacity: 0; transform: translateY(28px); transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1); }
.la-reveal.is-visible { opacity: 1; transform: none; }
.la-reveal-delay-1 { transition-delay: 0.08s; }
.la-reveal-delay-2 { transition-delay: 0.16s; }
.la-reveal-delay-3 { transition-delay: 0.24s; }

/* ---------------- CTAs ---------------- */
.la-cta-primary { display: inline-flex; align-items: center; gap: 12px; background: var(--la-red); color: #fff !important; text-decoration: none; font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: 15px; letter-spacing: 0.04em; padding: 18px 32px; border-radius: 999px; box-shadow: 0 12px 28px rgba(215,37,50,0.34); transition: transform 0.2s, box-shadow 0.2s, background 0.2s; border: 0; cursor: pointer; }
.la-cta-primary:hover, .la-cta-primary:focus-visible { background: var(--la-red-deep); transform: translateY(-2px); box-shadow: 0 16px 36px rgba(215,37,50,0.44); outline: none; }
.la-cta-primary .la-cta-arrow { font-weight: 900; transition: transform 0.2s; }
.la-cta-primary:hover .la-cta-arrow { transform: translateX(4px); }
.la-cta-sub { font-size: 13px; color: rgba(255,255,255,0.55); margin: 18px 0 0; }
.la-cta-row { margin-top: clamp(28px, 4vw, 44px); display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }

/* ---------------- Sticky CTA bar ---------------- */
.la-sticky-cta { position: fixed; bottom: 0; left: 0; right: 0; padding: 12px 16px env(safe-area-inset-bottom, 12px); background: rgba(30,30,30,0.92); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-top: 1px solid rgba(255,255,255,0.10); z-index: 9000; display: flex; align-items: center; justify-content: center; gap: 12px; transform: translateY(120%); transition: transform 0.4s cubic-bezier(0.22,1,0.36,1); pointer-events: none; }
.la-sticky-cta.is-visible { transform: translateY(0); pointer-events: auto; }
.la-sticky-cta .la-cta-primary { width: 100%; max-width: 480px; justify-content: center; padding: 14px 20px; font-size: 14px; box-shadow: 0 8px 22px rgba(215,37,50,0.5); }

@media (min-width: 900px) {
  .la-sticky-cta { left: auto; right: 24px; bottom: 24px; padding: 0; background: transparent; backdrop-filter: none; border: 0; }
  .la-sticky-cta .la-cta-primary { padding: 14px 22px; font-size: 14px; box-shadow: 0 10px 28px rgba(215,37,50,0.5); }
}

/* ---------------- Hero ---------------- */
.la-hero { background: var(--la-off-black); color: #fff; padding: clamp(80px, 11vw, 140px) 0 clamp(72px, 10vw, 124px); position: relative; overflow: hidden; }
.la-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 80% 30%, rgba(215,37,50,0.22), transparent 55%), radial-gradient(circle at 18% 80%, rgba(215,37,50,0.10), transparent 60%); pointer-events: none; }
.la-hero-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px); background-size: 56px 56px; mask-image: radial-gradient(ellipse at center, #000 30%, transparent 75%); -webkit-mask-image: radial-gradient(ellipse at center, #000 30%, transparent 75%); pointer-events: none; }
.la-hero > .la-container { position: relative; display: grid; gap: clamp(36px, 5vw, 64px); align-items: center; }
@media (min-width: 900px) { .la-hero > .la-container { grid-template-columns: 1.05fr 1fr; } }
.la-hero .la-eyebrow { color: #ff5a66; }
.la-h1 { font-family: Orbitron, Inter, system-ui, sans-serif; font-weight: 800; font-size: clamp(2.1rem, 5.4vw, 3.6rem); line-height: 1.06; letter-spacing: -0.01em; color: #fff; margin: 0 0 24px; max-width: 22ch; }
.la-subhead { font-size: clamp(1rem, 1.35vw, 1.16rem); line-height: 1.6; color: rgba(255,255,255,0.85); max-width: 60ch; margin: 0 0 36px; }

/* ---------------- Hero graphic (shared) ---------------- */
.la-hero-graphic { position: relative; width: 100%; aspect-ratio: 4 / 3; max-width: 540px; margin: 0 auto; }
.la-hero-graphic svg { width: 100%; height: 100%; display: block; }

/* Lead Agent: signals → pipeline */
@keyframes la-pulse { 0%, 100% { opacity: 0.45; transform: scale(0.9); } 50% { opacity: 1; transform: scale(1.05); } }
@keyframes la-glow { 0%, 100% { filter: drop-shadow(0 0 6px rgba(215,37,50,0.5)); } 50% { filter: drop-shadow(0 0 18px rgba(215,37,50,0.9)); } }
.la-hero-sig { animation: la-pulse 2.8s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }
.la-hero-sig:nth-child(2) { animation-delay: 0.4s; }
.la-hero-sig:nth-child(3) { animation-delay: 0.8s; }
.la-hero-sig:nth-child(4) { animation-delay: 1.2s; }
.la-hero-funnel { animation: la-glow 3.2s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }

/* Sales Agent: follow-up timeline */
@keyframes la-tl-fill { 0% { stroke-dashoffset: 380; } 60%, 100% { stroke-dashoffset: 0; } }
@keyframes la-tl-cycle { 0%, 100% { stroke-dashoffset: 380; } 60%, 95% { stroke-dashoffset: 0; } }
@keyframes la-bubble-in { 0%, 55% { opacity: 0; transform: translateY(8px) scale(0.9); } 65%, 95% { opacity: 1; transform: none; } 100% { opacity: 0; transform: translateY(8px) scale(0.9); } }
.la-tl-line { stroke-dasharray: 380; animation: la-tl-cycle 5.6s ease-in-out infinite; transform-box: fill-box; }
.la-tl-fire { animation: la-bubble-in 5.6s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }

/* ---------------- Sections ---------------- */
.la-section { padding: clamp(72px, 10vw, 120px) 0; position: relative; }
.la-section--light { background: var(--la-grey-light); color: var(--la-charcoal); }
.la-section--dark { background: var(--la-off-black); color: #fff; }
.la-section--dark .la-h2 { color: #fff; }
.la-section--dark .la-body { color: rgba(255,255,255,0.85); }
.la-section--dark .la-eyebrow { color: #ff5a66; }
.la-h2 { font-family: Orbitron, Inter, system-ui, sans-serif; font-weight: 800; font-size: clamp(1.7rem, 3.6vw, 2.5rem); line-height: 1.12; letter-spacing: -0.005em; margin: 0 0 24px; max-width: 22ch; color: var(--la-off-black); }
.la-body { font-size: clamp(1rem, 1.25vw, 1.1rem); line-height: 1.6; max-width: 62ch; margin: 0; }

/* ---------------- Steps (scroll-revealed) ---------------- */
.la-steps { list-style: none; margin: clamp(28px, 4vw, 40px) 0 0; padding: 0; display: grid; gap: clamp(22px, 3vw, 32px); position: relative; max-width: 820px; }
.la-step { display: grid; grid-template-columns: auto 1fr; gap: 22px; align-items: start; position: relative; }
.la-step::before { content: ''; position: absolute; left: 24px; top: 50px; bottom: -36px; width: 2px; background: linear-gradient(to bottom, rgba(215,37,50,0.4), rgba(215,37,50,0.04)); }
.la-step:last-child::before { display: none; }
.la-step__num { font-family: Orbitron, sans-serif; font-weight: 800; font-size: 16px; color: #fff; background: var(--la-red); border-radius: 50%; width: 48px; height: 48px; display: inline-flex; align-items: center; justify-content: center; line-height: 1; box-shadow: 0 8px 22px rgba(215,37,50,0.4); position: relative; z-index: 1; transition: transform 0.25s, box-shadow 0.25s; }
.la-step:hover .la-step__num { transform: scale(1.08); box-shadow: 0 12px 28px rgba(215,37,50,0.55); }
.la-step__title { font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: clamp(1.05rem, 1.5vw, 1.22rem); line-height: 1.4; margin: 8px 0 6px; color: inherit; }
.la-step__body { font-size: clamp(0.95rem, 1.15vw, 1.05rem); line-height: 1.6; margin: 0; color: inherit; opacity: 0.86; max-width: 60ch; }

/* ---------------- What you get (checks) ---------------- */
.la-checks { list-style: none; margin: clamp(28px, 4vw, 40px) 0 0; padding: 0; display: grid; gap: 14px; max-width: 760px; grid-template-columns: 1fr; }
@media (min-width: 720px) { .la-checks { grid-template-columns: 1fr 1fr; } }
.la-checks li { display: grid; grid-template-columns: auto 1fr; gap: 14px; font-size: clamp(0.95rem, 1.2vw, 1.05rem); line-height: 1.5; padding: 14px 16px; border-radius: 12px; background: rgba(0,0,0,0.04); }
.la-section--dark .la-checks li { background: rgba(255,255,255,0.05); }
.la-checks li::before { content: ''; display: block; width: 22px; height: 22px; border-radius: 50%; background: var(--la-red); margin-top: 2px; flex-shrink: 0; position: relative; }
.la-checks li::after { content: ''; position: absolute; left: 22px; top: 24px; width: 9px; height: 5px; border-left: 2px solid #fff; border-bottom: 2px solid #fff; transform: rotate(-45deg); }

/* ---------------- Stats band ---------------- */
.la-stats { display: grid; gap: clamp(20px, 3vw, 32px); margin-top: clamp(28px, 4vw, 44px); }
@media (min-width: 720px) { .la-stats { grid-template-columns: repeat(3, 1fr); } }
.la-stat { background: rgba(0,0,0,0.04); border: 1px solid rgba(0,0,0,0.06); border-radius: 18px; padding: clamp(22px, 3vw, 30px); }
.la-section--dark .la-stat { background: rgba(255,255,255,0.04); border-color: rgba(255,255,255,0.06); }
.la-stat__num { font-family: Orbitron, sans-serif; font-weight: 800; font-size: clamp(2.4rem, 5vw, 3.4rem); line-height: 1; color: var(--la-red); margin: 0; letter-spacing: -0.02em; display: inline-flex; align-items: baseline; gap: 2px; }
.la-stat__suffix { font-size: 0.62em; opacity: 0.85; }
.la-stat__label { font-size: clamp(0.95rem, 1.15vw, 1.02rem); line-height: 1.5; margin: 14px 0 12px; color: inherit; }
.la-stat__src { font-size: 11px; line-height: 1.45; color: rgba(0,0,0,0.55); margin: 0; font-style: italic; }
.la-section--dark .la-stat__src { color: rgba(255,255,255,0.55); }

/* ---------------- Compare bars ---------------- */
.la-compare { margin-top: clamp(36px, 5vw, 56px); max-width: 920px; }
.la-compare__title { font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: clamp(1rem, 1.3vw, 1.12rem); margin: 0 0 18px; opacity: 0.9; }
.la-bar { display: grid; grid-template-columns: 1fr; gap: 8px; margin: 0 0 22px; }
.la-bar__head { display: flex; justify-content: space-between; align-items: baseline; gap: 14px; font-size: clamp(0.9rem, 1.1vw, 1rem); }
.la-bar__label { font-weight: 600; }
.la-bar__pct { font-family: Orbitron, sans-serif; font-weight: 800; color: var(--la-red); }
.la-bar__track { height: 14px; background: rgba(0,0,0,0.08); border-radius: 999px; overflow: hidden; position: relative; }
.la-section--dark .la-bar__track { background: rgba(255,255,255,0.10); }
.la-bar__fill { display: block; height: 100%; width: 0; border-radius: 999px; background: linear-gradient(90deg, rgba(215,37,50,0.7), var(--la-red)); transition: width 1.6s cubic-bezier(0.22,1,0.36,1); }
.la-bar--against .la-bar__fill { background: linear-gradient(90deg, rgba(170,170,170,0.6), rgba(120,120,120,0.85)); }
.la-bar__note { font-size: 12px; line-height: 1.45; color: rgba(0,0,0,0.55); margin: 0; font-style: italic; }
.la-section--dark .la-bar__note { color: rgba(255,255,255,0.55); }

/* ---------------- Visibility preview (lead-agent: dashboard) ---------------- */
.la-dashboard { background: #11151c; border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 18px; max-width: 560px; box-shadow: 0 30px 80px rgba(0,0,0,0.4); margin: 0; overflow: hidden; }
.la-dashboard__head { display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 14px; }
.la-dashboard__title { font-family: Inter, system-ui, sans-serif; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.75); }
.la-dashboard__live { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; color: #5EEAD4; }
.la-dashboard__live::before { content: ''; width: 8px; height: 8px; border-radius: 50%; background: #5EEAD4; box-shadow: 0 0 8px #5EEAD4; animation: la-pulse 1.6s ease-in-out infinite; }
.la-dashboard__row { display: grid; grid-template-columns: 32px 1fr auto; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); opacity: 0; animation: la-row-in 0.6s forwards; }
.la-dashboard__row:last-child { border-bottom: 0; }
.la-dashboard__row:nth-child(2) { animation-delay: 0.1s; }
.la-dashboard__row:nth-child(3) { animation-delay: 0.4s; }
.la-dashboard__row:nth-child(4) { animation-delay: 0.7s; }
.la-dashboard__row:nth-child(5) { animation-delay: 1.0s; }
@keyframes la-row-in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.la-dashboard__avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #D72532, #AD1C24); display: flex; align-items: center; justify-content: center; font-family: Orbitron, sans-serif; font-weight: 800; color: #fff; font-size: 12px; }
.la-dashboard__meta { display: grid; gap: 2px; }
.la-dashboard__name { font-family: Inter, system-ui, sans-serif; font-weight: 600; color: rgba(255,255,255,0.95); font-size: 13px; }
.la-dashboard__sub { color: rgba(255,255,255,0.5); font-size: 11px; }
.la-dashboard__badge { font-family: Inter, system-ui, sans-serif; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; }
.la-dashboard__badge--sent { background: rgba(94, 234, 212, 0.15); color: #5EEAD4; }
.la-dashboard__badge--reply { background: rgba(255, 215, 0, 0.15); color: #F5C518; }
.la-dashboard__badge--book { background: rgba(215, 37, 50, 0.20); color: #ff7a86; animation: la-glow 2.2s ease-in-out infinite; }

/* ---------------- Scorecard (sales-agent) ---------------- */
.la-scorecard { background: #11151c; border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; padding: 20px; max-width: 560px; box-shadow: 0 30px 80px rgba(0,0,0,0.4); }
.la-scorecard__head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 16px; }
.la-scorecard__title { font-family: Inter, system-ui, sans-serif; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.75); }
.la-scorecard__count { font-family: Orbitron, sans-serif; font-size: 11px; color: rgba(255,255,255,0.5); }
.la-objection { display: grid; gap: 6px; margin-bottom: 14px; }
.la-objection__row { display: flex; justify-content: space-between; font-size: 13px; color: rgba(255,255,255,0.9); align-items: baseline; }
.la-objection__count { font-family: Orbitron, sans-serif; font-weight: 700; color: var(--la-red); }
.la-objection__bar { height: 8px; background: rgba(255,255,255,0.10); border-radius: 999px; overflow: hidden; }
.la-objection__fill { display: block; height: 100%; background: linear-gradient(90deg, rgba(215,37,50,0.7), var(--la-red)); border-radius: 999px; width: 0; animation: la-objfill 1.6s cubic-bezier(0.22,1,0.36,1) forwards; }
@keyframes la-objfill { to { width: var(--pct, 0%); } }

/* ---------------- Before/after toggle (sales-agent) ---------------- */
.la-toggle { display: grid; gap: 18px; max-width: 760px; margin-top: clamp(28px, 4vw, 40px); }
.la-toggle__switch { display: inline-flex; padding: 4px; background: rgba(0,0,0,0.08); border-radius: 999px; align-self: start; }
.la-section--dark .la-toggle__switch { background: rgba(255,255,255,0.10); }
.la-toggle__switch input { position: absolute; opacity: 0; pointer-events: none; }
.la-toggle__btn { font-family: Inter, system-ui, sans-serif; font-weight: 700; font-size: 13px; padding: 10px 18px; border-radius: 999px; cursor: pointer; color: inherit; opacity: 0.65; transition: background 0.25s, color 0.25s, opacity 0.25s; }
.la-toggle__btn.is-active { background: var(--la-red); color: #fff; opacity: 1; box-shadow: 0 4px 14px rgba(215,37,50,0.4); }
.la-toggle__panels { position: relative; min-height: 200px; }
.la-toggle__panel { padding: clamp(20px, 3vw, 28px); border-radius: 18px; background: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.06); display: none; }
.la-section--dark .la-toggle__panel { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.08); }
.la-toggle__panel.is-active { display: block; animation: la-fade 0.4s ease-out; }
@keyframes la-fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.la-toggle__panel--slip { border-left: 4px solid rgba(150,150,150,0.7); }
.la-toggle__panel--save { border-left: 4px solid var(--la-red); }
.la-toggle__caption { font-size: clamp(0.95rem, 1.2vw, 1.05rem); line-height: 1.55; margin: 0; }
.la-toggle__tag { display: inline-block; font-size: 10px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; margin-bottom: 12px; }
.la-toggle__panel--slip .la-toggle__tag { background: rgba(120,120,120,0.18); color: rgba(120,120,120,0.95); }
.la-toggle__panel--save .la-toggle__tag { background: rgba(215,37,50,0.18); color: var(--la-red); }

/* ---------------- Demo video slot ---------------- */
.la-video-slot { background: rgba(255,255,255,0.05); border: 2px dashed rgba(255,255,255,0.22); border-radius: 18px; aspect-ratio: 16 / 9; display: flex; align-items: center; justify-content: center; padding: 24px; max-width: 960px; margin: clamp(28px, 4vw, 40px) auto 0; }
.la-section--light .la-video-slot { background: rgba(0,0,0,0.04); border-color: rgba(0,0,0,0.18); }
.la-video-slot__placeholder { font-family: Inter, system-ui, sans-serif; font-size: 13px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.55); margin: 0; text-align: center; }
.la-section--light .la-video-slot__placeholder { color: rgba(0,0,0,0.55); }

/* ---------------- Final CTA ---------------- */
.la-section--final { background: linear-gradient(135deg, var(--la-red) 0%, var(--la-red-deep) 100%); color: #fff; text-align: center; }
.la-section--final .la-h2 { color: #fff; max-width: none; margin: 0 auto 18px; }
.la-section--final .la-body { color: rgba(255,255,255,0.92); margin: 0 auto; }
.la-section--final .la-cta-primary { background: #fff; color: var(--la-red) !important; box-shadow: 0 14px 32px rgba(0,0,0,0.22); margin-top: 28px; }
.la-section--final .la-cta-primary:hover { background: #fff; transform: translateY(-2px); box-shadow: 0 18px 40px rgba(0,0,0,0.28); }

/* ---------------- Two-col layout ---------------- */
.la-two-col { display: grid; gap: clamp(36px, 5vw, 56px); align-items: center; }
@media (min-width: 900px) { .la-two-col { grid-template-columns: 1fr 1fr; } }
.la-two-col--reverse > :first-child { order: 2; }
@media (max-width: 899px) { .la-two-col--reverse > :first-child { order: 0; } }

@media (max-width: 640px) {
  .la-h1 { font-size: clamp(1.9rem, 8.5vw, 2.2rem); }
  .la-h2 { font-size: clamp(1.45rem, 7vw, 1.7rem); }
  .la-step { grid-template-columns: 36px 1fr; gap: 14px; }
  .la-step__num { width: 36px; height: 36px; font-size: 13px; }
  .la-step::before { left: 17px; }
}
/* RA-LANDING-AGENT-CSS-END */
</style>
'''.strip()

TRACKER_SCRIPTS = '''
<!-- RA-LANDING-TRACKER-START -->
<script src="../assets/js/landing-config.js"></script>
<script src="../assets/js/landing-tracker.js"></script>
<script src="../assets/js/landing-animations.js"></script>
<!-- RA-LANDING-TRACKER-END -->
'''.strip()


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def cta(slot: str, label: str = CTA_LABEL, agent_id: str = '', extra_class: str = '') -> str:
    cls = 'la-cta-primary landing-cta'
    if extra_class:
        cls += ' ' + extra_class
    return (
        f'<a class="{cls}" data-cta="{esc(slot)}" data-page="{esc(agent_id)}" href="{CTA_HREF}">'
        f'{esc(label)} <span class="la-cta-arrow">→</span></a>'
    )


def sticky_cta(agent_id: str) -> str:
    return (
        '<div class="la-sticky-cta" aria-label="Book a strategy session">'
        + cta('sticky', agent_id=agent_id)
        + '</div>'
    )


# ----- Hero graphics (per-agent SVG) ---------------------------------------

LEAD_HERO_SVG = '''
<svg viewBox="0 0 540 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="la-funnel-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#D72532" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#D72532" stop-opacity="0.18"/>
    </linearGradient>
    <radialGradient id="la-output-glow">
      <stop offset="0" stop-color="#5EEAD4" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#5EEAD4" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- 4 signal sources on the left -->
  <g class="la-hero-sig">
    <circle cx="60" cy="80" r="14" fill="#D72532" opacity="0.85"/>
    <text x="86" y="84" fill="#fff" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">FUNDING ROUND</text>
  </g>
  <g class="la-hero-sig">
    <circle cx="60" cy="150" r="14" fill="#D72532" opacity="0.85"/>
    <text x="86" y="154" fill="#fff" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">NEW HIRE</text>
  </g>
  <g class="la-hero-sig">
    <circle cx="60" cy="220" r="14" fill="#D72532" opacity="0.85"/>
    <text x="86" y="224" fill="#fff" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">TECH SWITCH</text>
  </g>
  <g class="la-hero-sig">
    <circle cx="60" cy="290" r="14" fill="#D72532" opacity="0.85"/>
    <text x="86" y="294" fill="#fff" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">EXPANSION</text>
  </g>

  <!-- Animated dots flowing into the funnel -->
  <g fill="#ff7a86">
    <circle r="4"><animateMotion dur="3.2s" repeatCount="indefinite" path="M74,80 L300,185"/></circle>
    <circle r="4"><animateMotion dur="3.2s" begin="0.6s" repeatCount="indefinite" path="M74,150 L300,195"/></circle>
    <circle r="4"><animateMotion dur="3.2s" begin="1.2s" repeatCount="indefinite" path="M74,220 L300,205"/></circle>
    <circle r="4"><animateMotion dur="3.2s" begin="1.8s" repeatCount="indefinite" path="M74,290 L300,215"/></circle>
  </g>

  <!-- Funnel shape in the center -->
  <g class="la-hero-funnel" transform="translate(300,140)">
    <path d="M0,40 L160,40 L120,110 L120,160 L40,160 L40,110 z" fill="url(#la-funnel-grad)" stroke="#D72532" stroke-width="2"/>
    <text x="80" y="200" text-anchor="middle" fill="#fff" font-family="Orbitron,sans-serif" font-weight="800" font-size="12" letter-spacing="3" opacity="0.85">PIPELINE</text>
  </g>

  <!-- Output: qualified lead emerging -->
  <g transform="translate(430,200)">
    <circle r="36" fill="url(#la-output-glow)"/>
    <circle r="18" fill="#5EEAD4"/>
    <text y="60" text-anchor="middle" fill="#5EEAD4" font-family="Inter,sans-serif" font-weight="800" font-size="10" letter-spacing="2">QUALIFIED</text>
  </g>

  <!-- Output dot animation: signal exits funnel toward qualified -->
  <g fill="#5EEAD4">
    <circle r="5"><animateMotion dur="3.2s" begin="2.4s" repeatCount="indefinite" path="M380,200 L412,200"/></circle>
  </g>
</svg>
'''.strip()

SALES_HERO_SVG = '''
<svg viewBox="0 0 540 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <defs>
    <linearGradient id="la-tl-line-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#D72532"/>
      <stop offset="1" stop-color="#ff7a86"/>
    </linearGradient>
  </defs>

  <!-- Customer avatar with speech bubble -->
  <g transform="translate(60,80)">
    <circle cx="0" cy="0" r="28" fill="#1E1E1E" stroke="#D72532" stroke-width="2"/>
    <g stroke="#FFFFFF" stroke-width="2" fill="none">
      <circle cx="0" cy="-7" r="6"/>
      <path d="M-11,4 a11,11 0 0 1 22,0 v10 h-22 z"/>
    </g>
    <!-- Speech bubble -->
    <g transform="translate(48,-22)">
      <rect width="200" height="52" rx="10" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.25)"/>
      <text x="14" y="22" fill="#fff" font-family="Inter,sans-serif" font-size="12" font-weight="600">"Call me in a week —</text>
      <text x="14" y="40" fill="#fff" font-family="Inter,sans-serif" font-size="12" font-weight="600">need to talk to my partner."</text>
      <polygon points="0,18 -10,26 0,30" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.25)"/>
    </g>
  </g>

  <!-- Timeline horizontal axis -->
  <g transform="translate(60,240)">
    <line x1="0" y1="0" x2="420" y2="0" stroke="rgba(255,255,255,0.18)" stroke-width="2"/>
    <line x1="0" y1="0" x2="420" y2="0" stroke="url(#la-tl-line-grad)" stroke-width="3" class="la-tl-line"/>

    <!-- Day markers -->
    <g font-family="Inter,sans-serif" font-size="10" letter-spacing="1.2" font-weight="700" fill="rgba(255,255,255,0.65)">
      <g transform="translate(0,0)">
        <circle r="6" fill="#1E1E1E" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>
        <text y="26" text-anchor="middle">DAY 0</text>
      </g>
      <g transform="translate(140,0)">
        <circle r="6" fill="#1E1E1E" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>
        <text y="26" text-anchor="middle">DAY 3</text>
      </g>
      <g transform="translate(280,0)">
        <circle r="6" fill="#1E1E1E" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>
        <text y="26" text-anchor="middle">DAY 5</text>
      </g>
      <g transform="translate(420,0)">
        <circle r="8" fill="#D72532" stroke="#fff" stroke-width="2"/>
        <text y="28" text-anchor="middle" fill="#fff">DAY 7</text>
      </g>
    </g>
  </g>

  <!-- Message fires at day 7 -->
  <g transform="translate(380,160)" class="la-tl-fire">
    <rect width="148" height="60" rx="10" fill="#D72532"/>
    <text x="74" y="24" text-anchor="middle" fill="#fff" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">FOLLOW-UP SENT</text>
    <text x="74" y="44" text-anchor="middle" fill="rgba(255,255,255,0.85)" font-family="Inter,sans-serif" font-size="10">"Following up on our chat..."</text>
    <polygon points="60,60 74,72 88,60" fill="#D72532"/>
  </g>

  <!-- Label -->
  <text x="270" y="350" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-family="Inter,sans-serif" font-size="11" letter-spacing="2.4" font-weight="700">RIGHT TIME · RIGHT MESSAGE · EVERY TIME</text>
</svg>
'''.strip()


def render_hero(agent_id: str, cfg: dict) -> str:
    svg = LEAD_HERO_SVG if agent_id == 'lead-agent' else SALES_HERO_SVG
    return f'''
  <section class="la-hero">
    <div class="la-hero-grid"></div>
    <div class="la-container">
      <div>
        <span class="la-eyebrow la-reveal">{esc(cfg["eyebrow"])}</span>
        <h1 class="la-h1 la-reveal la-reveal-delay-1">{esc(cfg["hero_h1"])}</h1>
        <p class="la-subhead la-reveal la-reveal-delay-2">{esc(cfg["hero_subhead"])}</p>
        <div class="la-reveal la-reveal-delay-3">
          {cta('hero', agent_id=agent_id)}
          <p class="la-cta-sub">{esc(cfg["cta_sub"])}</p>
        </div>
      </div>
      <div class="la-hero-graphic la-reveal la-reveal-delay-2">{svg}</div>
    </div>
  </section>
'''.strip()


def render_steps(steps: list) -> str:
    out = []
    for i, step in enumerate(steps, 1):
        delay = min(2, i - 1)
        out.append(
            f'    <li class="la-step la-reveal la-reveal-delay-{delay}">\n'
            f'      <span class="la-step__num">{i:02d}</span>\n'
            f'      <div>\n'
            f'        <h3 class="la-step__title">{esc(step["title"])}</h3>\n'
            f'        <p class="la-step__body">{esc(step["body"])}</p>\n'
            f'      </div>\n'
            f'    </li>'
        )
    return '\n'.join(out)


def render_get_items(items: list) -> str:
    return '\n'.join(
        f'    <li class="la-reveal la-reveal-delay-{min(2, i)}">{esc(it)}</li>'
        for i, it in enumerate(items)
    )


def render_stats(stats: list) -> str:
    out = []
    for i, s in enumerate(stats):
        delay = min(2, i)
        out.append(
            f'    <div class="la-stat la-reveal la-reveal-delay-{delay}">\n'
            f'      <p class="la-stat__num"><span class="la-counter" data-target="{s["value"]}" data-duration="1400">0</span>'
            f'<span class="la-stat__suffix">{esc(s["suffix"])}</span></p>\n'
            f'      <p class="la-stat__label">{esc(s["label"])}</p>\n'
            f'      <p class="la-stat__src">Source: {esc(s["source"])}</p>\n'
            f'    </div>'
        )
    return '\n'.join(out)


def render_compare(compare_title: str, bars: list) -> str:
    rows = []
    for b in bars:
        kind = 'la-bar--with' if b['kind'] == 'with' else 'la-bar--against'
        rows.append(
            f'    <div class="la-bar {kind} la-reveal" data-pct="{b["pct"]}">\n'
            f'      <div class="la-bar__head"><span class="la-bar__label">{esc(b["label"])}</span>'
            f'<span class="la-bar__pct">{b["pct"]}%</span></div>\n'
            f'      <div class="la-bar__track"><span class="la-bar__fill"></span></div>\n'
            f'      <p class="la-bar__note">{esc(b["note"])}</p>\n'
            f'    </div>'
        )
    return (
        f'  <div class="la-compare">\n'
        f'    <p class="la-compare__title">{esc(compare_title)}</p>\n'
        + '\n'.join(rows) + '\n'
        f'  </div>'
    )


# ----- Visibility previews -------------------------------------------------

LEAD_DASHBOARD = '''
<div class="la-dashboard la-reveal">
  <div class="la-dashboard__head">
    <span class="la-dashboard__title">Live Pipeline</span>
    <span class="la-dashboard__live">Live</span>
  </div>
  <div class="la-dashboard__row">
    <span class="la-dashboard__avatar">MR</span>
    <div class="la-dashboard__meta"><span class="la-dashboard__name">Mara Rodriguez</span><span class="la-dashboard__sub">VP Sales · Northwind Co.</span></div>
    <span class="la-dashboard__badge la-dashboard__badge--book">Booked</span>
  </div>
  <div class="la-dashboard__row">
    <span class="la-dashboard__avatar">DK</span>
    <div class="la-dashboard__meta"><span class="la-dashboard__name">Devin Kim</span><span class="la-dashboard__sub">Founder · Helios Ops</span></div>
    <span class="la-dashboard__badge la-dashboard__badge--reply">Replied</span>
  </div>
  <div class="la-dashboard__row">
    <span class="la-dashboard__avatar">SE</span>
    <div class="la-dashboard__meta"><span class="la-dashboard__name">Sara Ellis</span><span class="la-dashboard__sub">COO · Trellis Group</span></div>
    <span class="la-dashboard__badge la-dashboard__badge--sent">Sent · 2m</span>
  </div>
  <div class="la-dashboard__row">
    <span class="la-dashboard__avatar">JT</span>
    <div class="la-dashboard__meta"><span class="la-dashboard__name">James Truong</span><span class="la-dashboard__sub">Director · Arcline</span></div>
    <span class="la-dashboard__badge la-dashboard__badge--sent">Sent · 11m</span>
  </div>
</div>
'''.strip()

SALES_SCORECARD = '''
<div class="la-scorecard la-reveal">
  <div class="la-scorecard__head">
    <span class="la-scorecard__title">Recurring Objections — last 30d</span>
    <span class="la-scorecard__count">Illustrative</span>
  </div>
  <div class="la-objection">
    <div class="la-objection__row"><span>"Need to talk to my partner"</span><span class="la-objection__count">42</span></div>
    <div class="la-objection__bar"><span class="la-objection__fill" style="--pct:92%"></span></div>
  </div>
  <div class="la-objection">
    <div class="la-objection__row"><span>"Pricing is over budget"</span><span class="la-objection__count">31</span></div>
    <div class="la-objection__bar"><span class="la-objection__fill" style="--pct:68%"></span></div>
  </div>
  <div class="la-objection">
    <div class="la-objection__row"><span>"Need it after Q3"</span><span class="la-objection__count">24</span></div>
    <div class="la-objection__bar"><span class="la-objection__fill" style="--pct:52%"></span></div>
  </div>
  <div class="la-objection">
    <div class="la-objection__row"><span>"Comparing two vendors"</span><span class="la-objection__count">18</span></div>
    <div class="la-objection__bar"><span class="la-objection__fill" style="--pct:38%"></span></div>
  </div>
  <div class="la-objection">
    <div class="la-objection__row"><span>"Already work with someone"</span><span class="la-objection__count">11</span></div>
    <div class="la-objection__bar"><span class="la-objection__fill" style="--pct:24%"></span></div>
  </div>
</div>
'''.strip()


def render_section_opener(agent_id: str, cfg: dict) -> str:
    return f'''
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["opener_title"])}</h2>
      <p class="la-body la-reveal la-reveal-delay-1">{esc(cfg["opener_body"])}</p>
      <div class="la-cta-row la-reveal la-reveal-delay-2">{cta('post-opener', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_steps(agent_id: str, cfg: dict) -> str:
    return f'''
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["steps_title"])}</h2>
      <ol class="la-steps">
{render_steps(cfg["steps"])}
      </ol>
      <div class="la-cta-row la-reveal">{cta('post-how-it-works', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_stats(agent_id: str, cfg: dict) -> str:
    return f'''
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["stats_title"])}</h2>
      <div class="la-stats">
{render_stats(cfg["stats"])}
      </div>
{render_compare(cfg["compare_title"], cfg["compare_bars"])}
      <div class="la-cta-row la-reveal">{cta('post-stats', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_get(agent_id: str, cfg: dict) -> str:
    return f'''
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["get_title"])}</h2>
      <ul class="la-checks">
{render_get_items(cfg["get_items"])}
      </ul>
      <div class="la-cta-row la-reveal">{cta('post-get', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_visibility(agent_id: str, cfg: dict) -> str:
    visual = LEAD_DASHBOARD if agent_id == 'lead-agent' else SALES_SCORECARD
    return f'''
  <section class="la-section la-section--light">
    <div class="la-container">
      <div class="la-two-col">
        <div>
          <h2 class="la-h2 la-reveal">{esc(cfg["see_title"])}</h2>
          <p class="la-body la-reveal la-reveal-delay-1">{esc(cfg["see_body"])}</p>
          <div class="la-cta-row la-reveal la-reveal-delay-2">{cta('post-visibility', agent_id=agent_id)}</div>
        </div>
        <div>{visual}</div>
      </div>
    </div>
  </section>
'''.strip()


# Before/after toggle for sales-agent only.
SALES_BEFORE_AFTER_TOGGLE = '''
<div class="la-toggle">
  <div class="la-toggle__switch" role="tablist">
    <label class="la-toggle__btn" data-for="slip" role="tab">
      <input type="radio" name="ba-toggle" value="slip">Without the agent
    </label>
    <label class="la-toggle__btn is-active" data-for="save" role="tab">
      <input type="radio" name="ba-toggle" value="save" checked>With the agent
    </label>
  </div>
  <div class="la-toggle__panels">
    <div class="la-toggle__panel la-toggle__panel--slip" data-panel="slip">
      <span class="la-toggle__tag">Deal slips</span>
      <p class="la-toggle__caption">Customer says "call me in a week." It gets buried under today's calls, then tomorrow's quote requests, then next week's payroll. By Day 7 it's been 9 days and no one remembers the conversation. By Day 14 they're talking to a competitor. The deal didn't die because they weren't interested.</p>
    </div>
    <div class="la-toggle__panel la-toggle__panel--save is-active" data-panel="save">
      <span class="la-toggle__tag">Deal saved</span>
      <p class="la-toggle__caption">Same customer, same "call me in a week." On Day 7, your rep gets a reminder with the full conversation context — the objection, the timing, the detail that matters. The follow-up message is built around their situation, not a generic blast. The call happens. The deal closes.</p>
    </div>
  </div>
</div>
'''.strip()


def render_section_built(agent_id: str, cfg: dict) -> str:
    extra = SALES_BEFORE_AFTER_TOGGLE if agent_id == 'sales-agent' else ''
    return f'''
  <section class="la-section la-section--dark">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["built_title"])}</h2>
      <p class="la-body la-reveal la-reveal-delay-1">{esc(cfg["built_for_body"])}</p>
      {extra}
      <div class="la-cta-row la-reveal">{cta('post-built', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_video(agent_id: str) -> str:
    return f'''
  <section class="la-section la-section--light">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">See it in action</h2>
      <div class="la-video-slot la-reveal la-reveal-delay-1" data-video-slot="{esc(agent_id)}-demo">
        <p class="la-video-slot__placeholder">DEMO VIDEO — RESERVED SLOT · EMBED COMING NEXT WEEK</p>
        <!-- TODO(Blaine): replace .la-video-slot innerHTML with embed -->
      </div>
      <div class="la-cta-row la-reveal" style="justify-content:center;">{cta('post-video', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_section_final(agent_id: str, cfg: dict) -> str:
    return f'''
  <section class="la-section la-section--final">
    <div class="la-container">
      <h2 class="la-h2 la-reveal">{esc(cfg["final_title"])}</h2>
      <p class="la-body la-reveal la-reveal-delay-1">{esc(cfg["final_body"])}</p>
      <div class="la-reveal la-reveal-delay-2">{cta('final', agent_id=agent_id)}</div>
    </div>
  </section>
'''.strip()


def render_body(agent_id: str, cfg: dict) -> str:
    return f'''
<main class="la-page">
{render_hero(agent_id, cfg)}
{render_section_opener(agent_id, cfg)}
{render_section_steps(agent_id, cfg)}
{render_section_stats(agent_id, cfg)}
{render_section_get(agent_id, cfg)}
{render_section_visibility(agent_id, cfg)}
{render_section_built(agent_id, cfg)}
{render_section_video(agent_id)}
{render_section_final(agent_id, cfg)}
{sticky_cta(agent_id)}
</main>
'''.strip()


# ---------------------------------------------------------------------------
# Head meta swap + body splice
# ---------------------------------------------------------------------------


def replace_head_meta(template: str, cfg: dict, canonical_url: str) -> str:
    template = re.sub(r'<title>.*?</title>',
                       f'<title>{esc(cfg["title_full"])}</title>',
                       template, count=1, flags=re.DOTALL)
    template = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{esc(cfg["description"])}">',
        template, count=1,
    )
    template = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical_url}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{esc(cfg["title_full"])}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{esc(cfg["description"])}">',
        template, count=1,
    )
    template = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical_url}">',
        template, count=1,
    )
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
    template = TEMPLATE_PATH.read_text(encoding='utf-8')

    if niche_id:
        canonical = f'https://revelationagency.com/{agent_id}/{niche_id}'
    else:
        canonical = f'https://revelationagency.com/{agent_id}'

    template = replace_head_meta(template, cfg, canonical)

    head_pos = template.find(HEAD_CLOSE)
    if head_pos < 0:
        raise RuntimeError('No </head> in template')
    template = template[:head_pos] + '\n' + LANDING_CSS + '\n' + template[head_pos:]

    nav_end = template.find(NAV_CLOSE)
    footer_open = template.find(FOOTER_OPEN)
    if nav_end < 0 or footer_open < 0:
        raise RuntimeError('Could not find nav/footer boundaries in template')
    nav_end += len(NAV_CLOSE)
    body = render_body(agent_id, cfg)
    template = template[:nav_end] + '\n\n' + body + '\n\n' + template[footer_open:]

    body_close = template.rfind(BODY_CLOSE)
    if body_close < 0:
        raise RuntimeError('No </body> in template')
    template = template[:body_close] + TRACKER_SCRIPTS + '\n' + template[body_close:]

    return template


def main():
    written = []
    for agent_id, cfg in PAGE_CONFIGS.items():
        out_dir = REPO / agent_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'index.html'
        page_html = render_page(agent_id, cfg, niche_id=None)
        out_path.write_text(page_html, encoding='utf-8')
        written.append((str(out_path.relative_to(REPO)), out_path.stat().st_size))

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
