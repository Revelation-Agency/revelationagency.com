# Copy migration manifest — P5 Revelation Agency rebrand

**Scope of this document.** For every meaningful copy surface, this file records whether the
existing wording is **preserved**, **replaced**, **retired**, or **deferred**, plus why. Anything
not listed here is preserved by default. No lorem-ipsum / brand-guide placeholder copy is
introduced anywhere.

## Global framing

- **Preserved:** Revelation Agency as a strategic growth partner; the "brand + acquisition + sales
  + CRM + automation + measurement work better as one system" thesis; conversation-first CTA;
  Clovis/Fresno + remote posture; The Reveal as the authority surface.
- **Replaced:** Every "Systems → Creative → Marketing" / "Strategy → Creative → Marketing" framing
  becomes "**Branding → Marketing → Sales**" (Canon 9487). Every top-level nav item, breadcrumb,
  service hub, portfolio hub, and homepage architecture diagram is updated.
- **Retired from primary experience:**
  - **Strategy Sprint** as the Revelation Agency flagship. Copy is preserved in migration archive
    URLs only; no promotion, no offer card, no CTA.
  - **Outsourced Marketing** as a top nav item. The `/services/marketing/outsource-marketing.html`
    file is redirected to the Marketing hub; no future personal-brand migration is asserted here.
  - The homepage **Tweaks** debug panel (source-visible in `index.html`, not intentionally gated
    for customers).
- **Deferred:** Any migration of Strategy Sprint / Outsourced Marketing to the Blaine McKenzie
  personal brand (packet: outside this scope; Canon 9541 keeps personal-brand site P3).

## Homepage (`index.html`)

| Element | Before | After |
|---|---|---|
| `<title>` | "Revelation Agency — Your Strategic Growth Partner" | Unchanged. Strategic growth partner is the doctrine-approved posture. |
| Hero H1 wording | keeps "Where growth becomes revelation." family | Unchanged. Compatible with new IA. |
| Hero trust chips | Systems · Creative · Marketing | **Branding · Marketing · Sales** |
| Architecture blueprint (SVG) heading + node labels | "Systems → Creative → Marketing" with nodes: Brand Systems / Sales Infrastructure / Digital Presence / AI & Automation on layer 01, Branding / Website / App / Video on layer 02, Digital Ads / Social / Search / Outsource on layer 03 | "**Branding → Marketing → Sales**" with nodes: Brand Strategy / Websites / Apps / Video on layer 01 (Branding), SEO & AI Visibility / Positioning / Social / Email on layer 02 (Marketing), Lead Gen / CRM / Follow-up / Conversion Ads on layer 03 (Sales). AI & Automation shown as a cross-cutting spine annotation, not a fourth layer. |
| Any "AI-powered" generic copy | none introduced; check no new instance | none introduced |
| "$500 website" / "starting at $500" | not present at baseline | remains absent (packet forbids it as the public anchor) |
| Tweaks / debug controls | `#tweaks-panel` block + JS | **Removed** |

## Global nav + footer (all pages carrying `RA-NAV-CANONICAL-START` marker)

| Slot | Before | After |
|---|---|---|
| Services L2 | Systems / Creative / Marketing | **Branding / Marketing / Sales** |
| Services L3 (Systems) | Brand Systems, Sales Infrastructure, Digital Presence, AI & Automation | Removed as an L2. Its leaves are redistributed. |
| Services L3 (Creative) | Branding, Website Development, App Development, Video Production | Moves under **Branding** as: Brand Strategy & Identity, Websites & Landing Pages, Apps & Digital Products, Video & Visual Content |
| Services L3 (Marketing) | Digital Ads, Social Media, Search & AI Rankings, Outsourced Marketing | Becomes: SEO & AI Visibility, Positioning / Content / Authority, Social Media, Email & Lifecycle Marketing |
| Services L3 (Sales, new) | — | Lead Generation & Personalized Outreach, CRM & Sales Infrastructure, Follow-up & Nurture, Conversion Advertising |
| Cross-cutting AI/automation link | in Systems L3 | Appears as a single non-nav link at the bottom of the Services drop and as a first-class page at `/services/ai-automation.html` — NOT a fourth pillar |
| Portfolio L2 | Systems Work / Creative Work / Marketing Work | Branding Work / Marketing Work / Sales Work |
| Primary CTA | Book a Free Strategy Session | Unchanged (conversation-first) |

## Service pillar hubs (new pages)

- `services/branding/index.html` — Branding as the identity + surface layer. Four leaves.
- `services/marketing/index.html` — Marketing as the visibility + demand layer. Four leaves. Retains URL.
- `services/sales/index.html` — Sales as the acquisition + revenue layer. Four leaves.
- `services/ai-automation.html` — cross-cutting explainer only; **not** a fourth pillar.

Copy for each hub is written from scratch here (no lorem-ipsum, no brand-guide placeholder). All
outcome language stays factual: what the pillar does, how it connects, how a prospect engages.

## Service leaves — copy source

For every new leaf under `services/{pillar}/…`, the copy uses:

1. The pillar's own explanatory content from the existing legacy leaf, when the topic maps
   directly (e.g., `services/creative/branding.html` copy is reframed into
   `services/branding/brand-strategy-identity.html`).
2. Freshly written framing paragraphs when there is no direct legacy source (all four Sales
   leaves, plus two new Marketing leaves).

No leaf claims a client outcome number that is not backed by the proof registry. When a
matching client case exists, it is linked; when it does not, the leaf shows a "how we work"
section instead.

## Portfolio (case-study copy)

- URLs are **retained** for every current case study (per proof migration ledger).
- **Trust Energy** outcome tiles (`$25 CPL`, `1:4 conv`, `4yr`) are replaced with a factual
  delivery-and-tenure description; no CPL / conversion / ROAS numbers are published.
- **Net Metering Systems** outcome tiles (`$50 CPL`, `25% conv`, `5x ROAS`) are replaced with a
  factual "systems shipped + operating scope" description. `12 automations` is retained only if
  screenshot evidence is attached later — for the current commit it is neutralized alongside
  the others.
- Everything else keeps its current copy.

## Typography decision

The updated brand references specify Horizon Bold as primary + Helvetica as secondary. The
Horizon font file is not licensed / staged in this checkout. To preserve the static-site
delivery advantage and avoid embedding a font we cannot legally distribute, the site keeps
the deployed **Bebas Neue** (Google Fonts CDN) + **Orbitron-VF** (self-hosted) heading cascade
and **Helvetica Neue / Helvetica / Arial** body cascade. This is recorded in
`artifacts/brand-asset-manifest.json`. When a licensed Horizon file becomes available, swapping
the `--font-head` token cascade will re-brand the entire site atomically.

## Tone-of-voice conventions used across all new copy

- Systems metaphor, not battlefield metaphor.
- Specific recognition + useful observation + grounded prescription + low-pressure invitation.
- No blanket "coded > WordPress/Wix/Squarespace" claim. Websites are framed as connected
  systems (governed iteration, disciplined technical SEO, analytics + CRM integration, versioned
  changes, ownership + portability).
- No "AI agency" positioning. AI/automation appears as a capability layer under all three pillars.
- No "autonomous selling", "instant response", or performance guarantees.
- Reviii is described as **managed** now; no public self-service API implication.
