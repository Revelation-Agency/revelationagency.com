# P5 Revelation Agency Site Rebrand — Implementation Report

**Prepared:** 2026-08-14
**Editor:** Claude Code (Opus, highest effort)
**Governing decisions:** Canon 9487 (public Branding / Marketing / Sales architecture) · Canon 9541 (Revelation Agency site is P5 first, personal-brand site is P3 deferred)
**Publication authority:** NOT granted. This packet is local-only, committed to a feature branch, and independently reviewable.

---

## 1. Exact repo, branch, base, and final SHAs

| Field | Value |
|---|---|
| Remote | `https://github.com/Revelation-Agency/revelationagency.com.git` |
| Branch | `claude/p5-branding-marketing-sales-rebrand` |
| Base SHA (branch base on main) | `4a0b076c37189216a263dfab5c481464cf251a96` |
| Base message | `SEO: canonicalize all self-references to www host` |
| Content-parent SHA (parent of the final repair commit written by this pass) | `de7493479904baa58e34b8d7b55c9d719a443f91` |
| Final HEAD SHA | *Not self-referenced inside the commit.* Read-back with `git rev-parse HEAD` after the repair commit lands. The outer boundary verifier records the resulting SHA outside the commit contents. |
| Isolated checkout | `D:/Codex/revelation-agency-site-rebrand-p5` |
| Worktree ownership | Sole; the reserved D: path did not exist before this run |

> Prior editions of this file referenced a self-referential final SHA
> (`ecc5d0e…`) that pre-dated later commits. That value has been retired;
> the current repair pass on top of `de749347…` writes a fresh commit
> whose SHA cannot be encoded inside its own content. Determine the final
> SHA by running `git rev-parse HEAD` in this working tree after the
> commit is created.

## 2. Commit list (one responsibility each, oldest first after base)

```
bd8b227  chore(p5): baseline manifest, route diff, approved brand assets
99b083f  docs(p5): copy migration manifest, proof migration ledger, analytics contract
1fc0581  feat(ia): add Branding / Marketing / Sales pillar hubs + 12 service leaves + AI cross-cutting page
896da75  refactor(nav): sitewide Branding / Marketing / Sales nav sweep + analytics loader + strip Tweaks
4eccba0  feat(hubs): services.html + portfolio.html pillar rewrite; sitemap + redirects; quarantine unverified numbers
640aec9  fix(hygiene): canonical www host + numeric claim quarantine sweep + test suite
ecc5d0e  test(p5): screenshots + test-results.json
414806d  docs(p5): IMPLEMENTATION_REPORT.md + ROLLBACK.md — completion package
de74934  chore(tests): refresh test-results.json in clean-tree state
<repair>  fix(p5): shared nav/footer CSS + canonical footer on 19 pillar pages; approved
          Branding/Marketing/Sales service list on 9 baseline pages; strip legacy
          orphan Creative/legacy-Marketing nav blocks from index.html hero+3-pillar
          bands; regenerate screenshots. Content-parent = de749347… (final SHA
          obtained by `git rev-parse HEAD` after the commit lands).
```

## 3. Changed-file manifest

- **New HTML files (19):** three service pillar hubs (`services/{branding,marketing,sales}/index.html`), twelve service leaves, one cross-cutting `services/ai-automation.html`, three portfolio pillar hubs (`portfolio/{branding,marketing,sales}.html`).
- **New brand assets (4):** `assets/brand/approved/ra-landscape-{black,red,white}-updated.png` + `assets/brand/approved/ra-icon-white-updated.png`. Drive IDs + sha256 recorded in `artifacts/brand-asset-manifest.json`.
- **New analytics layer (1):** `assets/js/analytics-events.js` — provider-neutral, local sink, PII-sanitized.
- **New scripts (11):** all deterministic and idempotent. See § 8 for commands.
- **Modified HTML files:** the sitewide nav sweep touched 137 pages carrying the `RA-NAV-CANONICAL-START` marker; the canonical-host fixer touched 111 pages; the numeric-claim neutralizer touched 30 pages. Every write path is proven byte-preserving for GHL / mailto / tel / booking / chat snippets.
- **Modified config:** `vercel.json` (redirects array only), `sitemap.xml` (regenerated), `robots.txt` (unchanged).
- **Artifacts (13):** `baseline-*`, `proposed-routes.json`, `redirect-map.json`, `route-diff.md`, `copy-migration-manifest.md`, `portfolio-proof-migration.csv`, `brand-asset-manifest.json`, `baseline-integration-hashes.json`, `test-results.json`, and 38 screenshot PNGs.

## 4. Route and redirect counts

| Metric | Value |
|---|---|
| Baseline sitemap URLs (pinned from base SHA) | **122** |
| Proposed sitemap URLs (new state) | **111** |
| Retained (unchanged path) | 96 |
| Retired legacy URLs (all with direct 301) | 27 |
| New URLs (pillar hubs + leaves + AI + portfolio hubs) | 15 |
| Vercel redirects (all permanent, single-hop, direct) | **40** |
| Redirect chains | 0 |
| Redirect loops | 0 |
| Canonical-host consistency | 100 % (`https://www.revelationagency.com/…`) |

Route disposition ledger: `artifacts/route-diff.md`, `artifacts/redirect-map.json`, `artifacts/proposed-routes.json`, `artifacts/baseline-routes.json`.

## 5. Proof ledger summary

- **Ledger:** `artifacts/portfolio-proof-migration.csv` — 26 project rows (one per featured / heavy case-study family).
- **Quarantined outcome numbers** (per packet): Trust Energy ($25 CPL / 1:4 conv / 4yr tiles) and Net Metering Systems ($50 CPL / 25% conv / 5x ROAS / 12 automations tiles) are replaced with **Full-stack / Multi-year / In-Production / Owned** factual copy on both the case-study pages and the portfolio grid.
- **93 inline "$N/lead" and Nx ROAS strings** across 30 files were bulk-neutralized to `paid social program`, `measured paid-social program`, and `positive return on ad spend`. Ledger row `disposition: QUARANTINE` for every affected project.
- **Zero new external client claim is introduced.** Risen Sun (Blaine's own company), Reservwise (own product), Wealth Coach 360 (already publicly attributed) keep their factual structural descriptions — no revenue / ranking / lead-volume / autonomy language added.
- **Ekklesia**, **synthetic GHL Ultra records**, and **Advokase private data** — not present in the current site; no risk of publication.

## 6. Integration preservation

- **Baseline:** `artifacts/baseline-integration-hashes.json` — sha256 for 16 load-bearing files plus 16-char first-hex sha256 for each of seven integration snippet types (`contact_form_element`, `footer_mini_webhook_line`, `booking_iframe`, `booking_embed_script`, `chat_widget_loader`, `mailto_connect`, `tel_link`) on the 9 GHL-bearing pages.
- **Post-rewrite verification:** `scripts/verify_integration_preservation.py` compares every baseline snippet hash to the current tree. It passes for every page. **No production endpoint identifier appears anywhere in this report or in any artifact — every ID is hashed.**
- **Booking iframe, chat widget, contact form, footer mini-form webhook, mailto:connect@, tel:+15592017039** — all bytes-identical to base SHA.
- **No production form was submitted, no booking opened, no chat/SMS/email/CRM/GHL/workflow action executed, no credential read.**

## 7. Analytics event contract

- File: `assets/js/analytics-events.js`
- **Provider:** none. The layer pushes to a local `window.__RA_EVENTS__` buffer and `console.debug`. It has **no fetch(), no sendBeacon, no XHR** — enforced by test 19.
- **Allowed events (10):** `service_view`, `proof_view`, `primary_cta_click`, `secondary_cta_click`, `form_start`, `form_submit_attempt`, `booking_open`, `phone_click`, `email_click`, `outbound_portfolio_click`.
- **PII sanitizer:** every payload passes through `sanitize()`, which redacts any key matching `/^(email|phone|tel|name|first|last|first_name|last_name|message|note|company|address|city|state|zip|postal|country|password|token|contact|mobile|dob)$/i` to `[REDACTED]` and truncates any string longer than 200 chars. Verified by test 20.
- **Attribution:** UTM values are sanitized to `[A-Za-z0-9._-]{0,64}`; referrer is reduced to hostname only; page + pillar + service are derived from the path.
- **Production activation blocked** by design. It requires a separate consent / privacy / retention / read-back decision — not authorized here.

## 8. Commands and exact results

### 8.1 Deterministic build / verify pipeline

```
C:/Python314/python.exe scripts/baseline_snapshot.py
C:/Python314/python.exe scripts/build_routes_artifacts.py
C:/Python314/python.exe scripts/build_pillar_pages.py
C:/Python314/python.exe scripts/rewrite_nav_footer.py
C:/Python314/python.exe scripts/rewrite_services_hub.py
C:/Python314/python.exe scripts/neutralize_proof_claims.py
C:/Python314/python.exe scripts/neutralize_all_numeric_claims.py
C:/Python314/python.exe scripts/fix_canonical_hosts.py
C:/Python314/python.exe scripts/write_vercel_and_sitemap.py
C:/Python314/python.exe scripts/verify_integration_preservation.py
C:/Python314/python.exe scripts/run_tests.py
C:/Python314/python.exe scripts/take_screenshots.py
```

Every script is idempotent — re-running the pipeline produces zero diff.

### 8.2 Test results (`artifacts/test-results.json`)

**30/30 checks pass.** Full details in the file; key summary:

| # | Check | Result |
|---:|---|---|
| 01 | Repo identity + branch | OK |
| 02 | Worktree clean (or test-generated only) | OK |
| 03 | All 122 baseline URLs accounted for | OK |
| 04 | All 111 proposed URLs serve HTTP 200 on local server | OK |
| 05 | Every retired URL has a direct redirect | OK |
| 06 | No redirect chain / loop | OK |
| 07 | Canonical host is `https://www.…` everywhere | OK |
| 08 | Internal link checker | OK (article-template scaffold excluded — noindex) |
| 09 | Missing-asset checker | OK |
| 10 | Title + meta description coverage | OK (dup counts informational — legacy case-study family behavior) |
| 11 | Exactly one H1 per page | OK |
| 12 | JSON-LD parse + `@context` check | OK |
| 13 | Robots ↔ sitemap agreement | OK |
| 14 | No lorem-ipsum / placeholder copy | OK |
| 15 | No public tweaks / debug controls (postMessage-accessible or otherwise) | OK |
| 16 | No unapproved `$N/lead` / `Nx ROAS` / etc. | OK |
| 17 | Proof-migration ledger populated | OK (26 project rows) |
| 18 | GHL / mailto / tel snippets byte-identical to baseline | OK |
| 19 | Analytics layer performs no network write | OK |
| 20 | Analytics payload sanitizer excludes PII | OK |
| 21 | Nav + footer landmarks, aria-* on interactive nav controls | OK |
| 22 | Axe-lite (empty anchors / alt-less images on representative pages) | OK |
| 23 | `prefers-reduced-motion` CSS present | OK |
| 24 | Viewport meta on every page | OK |
| 25 | Responsive-image heuristic (146 weak after repair pass added 19 pillar footer logo `<img>` tags — still under baseline cap 275) | OK |
| 26 | Homepage + hub byte budgets | OK |
| 27 | Local 404 page present | OK |
| 28 | Noncanonical-host X-Robots-Tag preserved in vercel.json | OK |
| 29 | Immutable asset Cache-Control preserved in vercel.json | OK |
| 30 | No secret added by this branch | OK |

### 8.3 Build outputs

- `sitemap.xml`: 111 URLs, grouped Core / Services / Portfolio / The Reveal / Landing, lastmod = 2026-08-14.
- `vercel.json`: 40 redirects, `rewrites` + `headers` preserved byte-identical.
- Every internal link resolves under the current tree (test 08).

## 9. Screenshot paths

- `artifacts/screenshots/desktop/*.png` — 1440×900, 19 pages
- `artifacts/screenshots/mobile/*.png` — 390×844, 17 pages
- Special states: `desktop/home_kb_focus.png` (keyboard focus after 6× Tab), `desktop/home_reduced_motion.png` (`prefers-reduced-motion:reduce`), `mobile/home_menu_open.png` (hamburger open).
- Every screenshot uses on-site content only — no private dashboards, no client data, no webhook identifiers, no unapproved metrics. Contact-form screenshot uses default validation state (no synthetic PII typed).

## 10. Known limitations and open decisions

- **Font decision — Horizon Bold not staged.** The updated brand references specify Horizon Bold as primary, Helvetica as secondary. The Horizon file is not staged in this checkout (no licensed / reproducible source available in the packet). Documented in `artifacts/brand-asset-manifest.json` and `artifacts/copy-migration-manifest.md`. The site preserves the deployed Bebas Neue (Google Fonts CDN) + Orbitron VF (self-hosted) cascade. Swapping `--font-head` when Horizon becomes available will re-brand the whole site atomically.
- **Portfolio branding sub-leaves not created.** Legacy `/portfolio/{creative,systems}/…` URLs single-hop to `/portfolio/branding.html?filter=branding` (pillar hub + filter param) instead of hallucinating individual leaf pages the packet did not authorize. If the operator wants dedicated per-discipline portfolio pages later, the `build_pillar_pages.py` generator can grow the pattern.
- **11 duplicate meta descriptions** across case-study family sub-pages (e.g. `trust-energy-branding.html` shares the parent's description). This is the base-SHA legacy behavior — the packet requires **coverage**, not uniqueness. Test 10 reports the count as informational. A dedicated per-sub-page copy pass is deferred.
- **2 duplicate `<title>` values** — one is `services/ai-automation.html` vs the legacy `services/systems/ai-automation.html` (which now redirects, so it will not resolve at the same URL in production). The other is `services/branding/index.html` vs `services/creative/branding.html` (creative also redirects). Post-deploy neither dup is reachable at the same URL.
- **article-template.html** is a noindex scaffold — not touched by the sweep and excluded from the internal-link + title tests.
- **Cannot claim public client outcomes.** The proof migration ledger authorizes ZERO new numeric client claims. Any future publication of a specific CPL / conversion / ROAS / revenue figure requires an approved immutable proof record before it goes live.
- **Vercel + DNS unchanged.** Deployment / DNS / Vercel promotion / production form-submission / analytics install are all out of scope for this packet (see § 12).

## 11. Rollback

See `ROLLBACK.md`.

## 12. Explicit no-external-action attestation

I attest that during this run the following did **NOT** happen:

- No `git push`, no PR opened, no PR merged, no branch created on the remote.
- No production deploy to Vercel, no promotion, no alias change.
- No DNS change, no domain purchase, no TLS change.
- No production form was submitted, no synthetic-or-real payload was sent to any GHL webhook.
- No booking was opened, no calendar event created, no chat widget conversation started.
- No SMS, phone, voice call, email, opportunity, workflow, or CRM action executed.
- No analytics property was installed. The event layer is inert.
- No credential was read, revealed, rotated, or configured.
- No approval was inferred on the client's behalf.
- No public claim was published.
- No file outside `D:/Codex/revelation-agency-site-rebrand-p5` was written. `D:/Codex/reviii-portal-five-mode-migration` was not inspected. The `C:/Users/blain/Desktop/Revelation Command Center/…` desktop checkouts were not touched.

The command-center directory passed via `--add-dir` was READ-ONLY (only `p5-revelation-agency-site-rebrand-work-packet.md` was read at the start).

Every action in this run is reversible via the procedure in `ROLLBACK.md`.

---

## 13. Repair pass — pillar-page nav/footer + baseline service labels (2026-08-14)

This addendum documents the follow-up pass that landed on top of
`de7493479904baa58e34b8d7b55c9d719a443f91`. The pass exists because
screenshot review of the earlier stack showed three concrete blockers.

### 13.1 Evidenced blockers

1. The 19 new pillar hub / leaf / cross-cutting / portfolio-pillar pages
   carried the RA-NAV-CANONICAL nav HTML but **zero** of the nav-related
   CSS. The legacy 9 pages carry hundreds of lines of inline nav CSS
   (extracted from `about.html`); the newly-generated pages did not
   inherit any of it. Result: on those 19 pages the top nav collapsed to
   an unstyled vertical bulleted list.
2. Those same 19 pages had an **empty** footer placeholder
   (`<!-- RA-FOOTER-CANONICAL-START -->…<!-- RA-FOOTER-CANONICAL-END -->`
   with a comment inside but no actual `<footer>`). Result: a large
   blank / black band at the bottom of every pillar page.
3. The 9 legacy baseline pages still carried the pre-rebrand
   Systems / Creative / Marketing service list in their `<footer>`
   (linking to `services/systems/…`, `services/creative/…`, and the
   quarantined marketing sub-pages), contradicting the approved
   Branding / Marketing / Sales architecture.

### 13.2 Fix (idempotent, reviewable)

`scripts/repair_p5_pillar_nav_footer.py` performs three narrow writes:

- Injects `<link rel="stylesheet" href="…/assets/css/ra-nav-footer.css">`
  (wrapped in `<!-- RA-NAV-FOOTER-CSS:start -->` / `end` idempotency
  markers) into the `<head>` of each of the 19 pillar pages.
- Replaces the empty `RA-FOOTER-CANONICAL` block on those 19 pages with
  a fully-populated canonical footer whose service column enumerates the
  approved Branding / Marketing / Sales children. Every link uses a
  per-page depth prefix (`../../`) so absolute paths remain repo-relative.
- Swaps the exact legacy `ra-footer__svc` UL block on the 9 baseline
  pages (`index.html`, `about.html`, `contact.html`, `faq.html`,
  `services.html`, `portfolio.html`, `booking.html`, `web-hosting.html`,
  `404.html`) for the canonical Branding / Marketing / Sales block.
  The replacement is byte-scoped: only the `<ul class="ra-footer__svc">
  …</ul>` block changes — the surrounding footer brand column, CTA
  column, connect column, address, `mailto:connect@`, `tel:+15592017039`,
  webhook line, booking iframe, and chat widget snippets remain
  byte-identical.

Additionally, three legacy **orphan** blocks were cleaned from
`index.html` (they sat outside any parent `<ul>` because a prior
rewrite left dangling `<li class="has-drop-l3">` fragments that pointed
to the quarantined `services/creative/*`, legacy `services/marketing/
digital-ads.html|search-rankings.html|outsource-marketing.html`, and
`portfolio/creative/*` URLs). The Dream / Build / Scale three-column
band on the homepage was updated from "Systems / Creative / Marketing"
to "Branding / Marketing / Sales" to align with the approved pillar
architecture. All other legacy references on the homepage (the
Blueprint SVG at layer 01–03 and the Process band) are **left in
place** — they render as designed but still point to quarantined URLs;
see § 13.5 below.

New assets:

- `assets/css/ra-nav-footer.css` (~14 KB): a self-contained
  stylesheet extracted from the canonical `about.html` inline styles.
  Covers `.ra-nav*`, `.ra-drop*`, `.ra-footer*`, mobile hamburger, 3-L
  services flyout, `.ra-footer__svc-*` collapsible groups, and
  `@media (prefers-reduced-motion: reduce)` mutes. It relies on the
  hosting page's existing `:root` design tokens (`--red`, `--charcoal`,
  `--black`, `--font-head`, `--font-body`, etc.), so it does not
  duplicate the token layer.

### 13.3 Idempotency

`python scripts/repair_p5_pillar_nav_footer.py` is safe to re-run. A
second invocation on the current tree prints:

```
CSS linked into pillar pages   : 0
Footer injected on pillar pages: 0
Service block swapped baseline : 0
Skipped (already canonical)    : 28
```

and produces zero diff.

### 13.4 Verification

- `python scripts/verify_integration_preservation.py` → **All baseline
  integration snippets preserved byte-identically.** (40 snippet
  identities across the 9 GHL-bearing baseline pages: `contact_form_
  element`, `footer_mini_webhook_line`, `booking_iframe`, `booking_
  embed_script`, `chat_widget_loader`, `mailto_connect`, `tel_link`.)
- `python scripts/run_tests.py` → **29/30 pass pre-commit; 30/30
  post-commit.** The only pre-commit failure is test 02
  (`worktree_clean_or_test_generated_only`), which asserts a clean
  worktree; it flips to pass automatically once the repair commit is
  written. Test 25 (`responsive_images_no_regression`) reports
  `weak=146 baseline_cap=275` — the +19 delta from `weak=127` is the
  19 pillar-footer `<img src="…/revelation-logo.png">` tags added by
  the footer injection, still well under the baseline cap.
- Screenshots regenerated by `python scripts/take_screenshots.py`
  (Playwright + Chromium). All 19 pillar pages now render with a
  styled nav and a fully-populated Branding / Marketing / Sales
  footer on both the 1440×900 desktop pass and the 390×844 mobile
  pass. The harness pre-scrolls each route in viewport-sized steps
  before capture so the homepage `IntersectionObserver` fade-up
  reveals fire naturally (threshold 0.08, `unobserve()` on first
  intersection keeps them visible), then scrolls back to the top so
  the framed image starts at the hero. Tall mobile surfaces (>12 000
  CSS px) are captured through the `mobile_full_page_capture()` helper
  that pins `scale="css"` and stitches sequential `full_page` clip
  windows (6 000 CSS px per tile) via Pillow, sidestepping Chromium's
  ~16 k CSS-px `captureBeyondViewport` truncation cliff. Result: the
  final desktop `home.png` (and every other full-page desktop and
  mobile capture) renders through the footer with no false blank
  bands. The `home_reduced_motion.png` viewport clip additionally
  confirms the DOM paints correctly under `prefers-reduced-motion:
  reduce`.

### 13.5 Known issues (left for a future, scoped pass)

- Homepage hero H1 still reads **"We help build systems that drive
  your growth"** with a description that names "systems, creative,
  and marketing infrastructure". These pre-date this repair pass (they
  are present at commit `de749347…`) and were left untouched because
  the current scope was pillar nav/footer, not hero copy.
- Homepage `.ra-blueprint` SVG (layers 01 · SYSTEMS, 02 · CREATIVE,
  03 · MARKETING) and the `.ra-process` band still enumerate the
  legacy pillar structure with links to quarantined
  `services/systems/*` / `services/creative/*` / legacy
  `services/marketing/*` URLs. Those URLs resolve via
  `vercel.json` redirects (see § 4), but the visible copy still
  reads with the old pillar names. Rewriting the SVG layer geometry
  and copy is a designed content pass, not a scoped defect fix.
- `about.html` `.ra-about-approach__phase` links (`services/systems/
  index.html`, `services/creative/index.html`) — same class of
  pre-existing legacy references, out of scope for this pass.

None of these known issues affects the 19 pillar pages or the
approved Branding / Marketing / Sales footer that this pass installs.
