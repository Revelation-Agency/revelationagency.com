# Revelation Agency 2026 Refresh — Implementation Report

**Prepared:** 2026-08-17

**Implementation:** Codex primary, with independent Claude Opus adversarial review

**Governing decisions:** Revelation Agency is the done-for-you Branding / Marketing / Sales operator; AI and automation are cross-cutting capabilities, not a fourth public pillar
**Publication authority:** Not granted. This report covers a local candidate only.

## 1. Repository and release boundary

| Field | Value |
|---|---|
| Remote | `https://github.com/Revelation-Agency/revelationagency.com.git` |
| Branch | `claude/p5-branding-marketing-sales-rebrand` |
| Main baseline | `4a0b076c37189216a263dfab5c481464cf251a96` |
| Candidate parent at start of this pass | `1e3f0436bc7bcf7c57be09e61cd640ee5ce85ee3` |
| Final candidate HEAD | Read with `git rev-parse HEAD`; a commit cannot safely contain its own SHA |
| Isolated checkout | `D:/Codex/revelation-agency-site-rebrand-p5` |

No push, pull request, merge, Vercel deploy, alias change, DNS change, form
submission, booking, chat, email, SMS, CRM, or workflow action was performed.

## 2. Delivered outcome

The site now presents one coherent public architecture:

- **Branding:** Brand Strategy & Identity; Websites & Landing Pages; Apps &
  Digital Products; Video & Visual Content.
- **Marketing:** SEO & AI Visibility; Positioning, Content & Authority; Social
  Media; Email & Lifecycle Marketing.
- **Sales:** Lead Generation & Personalized Outreach; CRM & Sales
  Infrastructure; Follow-up & Nurture; Conversion Advertising.
- **AI & Automation:** governed, cross-cutting implementation inside the three
  pillars rather than a standalone fourth pillar.

This architecture is reflected in navigation, footers, service hubs and leaves,
homepage messaging, The Reveal, portfolio filters, case-study metadata, social
metadata, and structured data.

## 3. New identity and visual system

The two user-supplied transparent RA logo PNGs are preserved byte-for-byte under
`assets/brand/current/source/`. Their SHA-256 values are pinned in
`assets/brand/current/manifest.json` and enforced by
`scripts/verify_2026_refresh.py`.

Generated current-brand outputs include:

- compact red RA navigation mark;
- red/black agency lockup for footers;
- favicon and application-icon set;
- 1200×630 social preview card;
- compatibility output at `assets/revelation-logo.png` for retained templates.

The shared design layer is `assets/css/ra-refresh-2026.css` and
`assets/js/ra-refresh-2026.js`, cache-busted as `v=20260817c` on all 140 HTML
files. It provides the black/off-white/#C91C1D system, connected-growth hero,
portfolio card treatment, responsive navigation, restrained motion, reduced-
motion behavior, and mobile chat containment.

### First-party editorial imagery

Six premium 1672×941 images were generated with OpenAI ImageGen and optimized
to WebP. Their prompts, usage, byte sizes, and SHA-256 hashes are recorded in
`assets/brand/visuals/2026/manifest.json`.

| Asset | Public use |
|---|---|
| `branding-signal.webp` | Branding hub and four Branding leaves |
| `marketing-signal.webp` | Marketing hub and four Marketing leaves |
| `sales-signal.webp` | Sales hub and four Sales leaves |
| `ai-automation-signal.webp` | AI & Automation cross-cutting hero |
| `reveal-straight-answers.webp` | Reveal card and article hero |
| `reveal-video-infrastructure.webp` | Reveal card and article hero |

The service compositions reserve dark left-side space for readable headings and
place detail on the right. Desktop uses a slow background drift; mobile and
`prefers-reduced-motion` disable it. The assets total under 500 KB after WebP
optimization and are assigned to 18 public pages through explicit,
generator-owned `data-ra-visual` attributes.

## 4. Portfolio migration

`assets/data/portfolio-taxonomy-2026.json` is the canonical portfolio source of
truth. It contains:

- **68** case-study records;
- **21** master projects;
- a primary discipline, all mapped B/M/S disciplines, pillar membership, and
  cross-cutting AI flag for every case;
- exact master-card data used by the main portfolio and pillar shelves.

Current card/filter counts are:

| Surface | Projects |
|---|---:|
| All | 21 |
| Branding | 21 |
| Marketing | 8 |
| Sales | 12 |
| Multi-pillar masters | 14 |

The three pillar shelves are manifest-derived and exact. Trust Energy appears
once on each Branding, Marketing, and Sales shelf, matching its mapped
disciplines. Case pages include visible discipline chips and valid
`CreativeWork` JSON-LD. Retired Systems / Creative / Strategy taxonomy remains
only in redirect-intent historical files, never on a public successor route.

## 5. Routing and search contract

- **111** clean canonical `https://www.revelationagency.com` sitemap URLs;
- **35** direct migration redirects;
- one host-conditioned permanent apex-to-`www` redirect;
- two clean Bill Gerard alias rewrites;
- `cleanUrls: true` and `trailingSlash: false`;
- zero redirect chains, loops, or unresolved local destinations;
- 27 retained legacy documents are redirect-only and canonicalize directly to
  their successors.

`scripts/build_routes_artifacts.py` and
`scripts/write_vercel_and_sitemap.py` own this contract. The older sitemap and
pillar/page authors fail closed so they cannot restore `.html` canonicals, the
apex host, or retired taxonomy.

## 6. Proof and integration safety

The proof ledger authorizes delivery facts, not new outcome claims. Public Net
Metering Systems, Trust Energy, and Highlands Energy pages were checked against
route-scoped quarantine patterns. Unsupported CPL, conversion, ROAS, tenure,
automation-count, and benchmark claims are absent.

Production integration snippets remain byte-identical to the pinned baseline:

- contact form element and footer mini-form webhook line;
- booking iframe and embed script;
- chat widget loader;
- `mailto:connect@revelationagency.com` and `tel:+15592017039`.

The analytics helper remains provider-neutral and performs no network write.
No secret was added by this branch.

## 7. Supported deterministic pipeline

Run from the repository root:

```powershell
python scripts/build_2026_brand_assets.py
python scripts/apply_2026_site_refresh.py
python scripts/apply_2026_portfolio_taxonomy.py
python scripts/build_routes_artifacts.py
python scripts/write_vercel_and_sitemap.py
python scripts/verify_integration_preservation.py
python scripts/verify_2026_refresh.py --max-errors 0
python scripts/run_tests.py
python scripts/take_screenshots.py
```

Both 2026 HTML rewriters are idempotent. A second run must report zero changed
HTML, case-study, shelf, and proof files.

Retired scripts that intentionally fail closed:

- `scripts/build_landing_pages.py`
- `scripts/build_pillar_pages.py`
- `scripts/regen_sitemap.py`
- `scripts/repair_p5_pillar_nav_footer.py`
- `scripts/rewrite_nav_footer.py`

## 8. Verification evidence

Pre-commit local evidence for the final content tree:

- `scripts/verify_2026_refresh.py --max-errors 0`: **16/16 pass**;
- legacy suite: **29/30 pass**, with only the intentional clean-worktree gate
  failing before the candidate commit;
- generated visual validation: six WebP containers, all hashes match the
  visual manifest, all six referenced in the shared stylesheet, all 18 page
  assignments present;
- responsive visual probe: 12 representative routes at 390px and 320px,
  **24/24 clean** with no horizontal overflow, local 4xx, or page errors;
- main portfolio filters: 21 / 21 / 8 / 12 for All / Branding / Marketing /
  Sales;
- `git diff --check`: clean.

After the implementation commit, `scripts/run_tests.py` is rerun from a clean
tree. Its machine-readable result is `artifacts/test-results.json`; the final
evidence commit records the clean-tree receipt.

### Independent Claude Opus review

Two read-only Opus passes were run at maximum effort. The first found Trust
Energy missing from the three pillar shelves. The second verified that repair,
the six-image visual layer, hashes, routing, taxonomy, proof safety, and
generator guardrails. It then found one visible `Brand Systems` label and four
retired `data-cat` values on `services.html`; those were moved to the 2026
vocabulary at the generator level and added to the verifier's public-taxonomy
gate.

## 9. Screenshot evidence

`python scripts/take_screenshots.py` regenerates the final packet from a local
127.0.0.1 server:

- `artifacts/screenshots/desktop/`: 19 representative full pages plus keyboard-
  focus and reduced-motion states;
- `artifacts/screenshots/mobile/`: the same 19 page surfaces at 390×844 plus an
  open-menu state.

The harness pre-scrolls pages so reveal animations settle and tiles very tall
mobile captures to avoid Chromium's long-page truncation. It uses public/on-site
content only and does not submit forms or interact with external services.

## 10. Known limits and deferred decisions

- Horizon Bold was referenced in the brand discussion but no licensed,
  reproducible font file was supplied. The current Bebas Neue / Orbitron / sans
  stack remains in place.
- Retained legacy HTML exists only to support direct redirect migration and is
  excluded from public taxonomy checks.
- A small number of case-study family pages share meta descriptions. Coverage,
  canonical URLs, and titles are valid; discipline-specific description
  refinement is a future SEO polish pass.
- Publication remains a separate authorization gate. Local completion is not a
  production deployment.

## 11. Final local handoff

The candidate is locally complete when all of the following are true:

1. supported rewriters converge on a second run;
2. the 16-check refresh verifier passes;
3. the implementation commit is written;
4. the 30-test suite passes from the clean tree;
5. the evidence-only receipt commit is written;
6. `git status --short` is empty.

No production action is implied by this handoff. Push, pull request, merge, and
deployment require a separate explicit instruction.
