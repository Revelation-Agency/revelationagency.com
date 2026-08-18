# Revelation Agency 2026 Refresh — Rollback Plan

## Scope and authority

This plan covers the local feature-branch candidate and a future production
release if one is separately authorized. No push, merge, Vercel deployment,
alias change, or DNS change was performed during the refresh.

Repository boundary:

- branch: `claude/p5-branding-marketing-sales-rebrand`;
- main baseline: `4a0b076c37189216a263dfab5c481464cf251a96`;
- candidate parent at the start of the final pass:
  `1e3f0436bc7bcf7c57be09e61cd640ee5ce85ee3`;
- final candidate SHA: read with `git rev-parse HEAD` after the evidence commit.

## 1. Preserve before any rollback

Create a recoverable branch bundle before changing history or removing the
isolated checkout:

```powershell
git status --short
git log --oneline --decorate -12
git bundle create D:/Codex/revelation-agency-site-rebrand-p5-backup.bundle `
  claude/p5-branding-marketing-sales-rebrand
git bundle verify D:/Codex/revelation-agency-site-rebrand-p5-backup.bundle
```

Also preserve the `artifacts/` directory. It contains the pinned baseline,
route disposition, proof ledger, taxonomy migration, integration hashes, test
receipt, and desktop/mobile screenshots.

## 2. Complete refresh inventory

A rollback must account for all of these 2026-owned surfaces, not only the HTML
files:

- `assets/brand/current/` — supplied-logo sources, generated logo roles,
  favicons, and social card;
- `assets/brand/visuals/2026/` — six generated editorial WebPs and prompt/hash
  manifest;
- `assets/css/ra-refresh-2026.css` and
  `assets/js/ra-refresh-2026.js`;
- `assets/data/portfolio-taxonomy-2026.json`;
- `artifacts/portfolio-taxonomy-migration-2026.csv` plus route/proof/test and
  screenshot artifacts;
- `scripts/build_2026_brand_assets.py`;
- `scripts/apply_2026_site_refresh.py`;
- `scripts/apply_2026_portfolio_taxonomy.py`;
- `scripts/verify_2026_refresh.py`;
- 140 HTML documents, `vercel.json`, `sitemap.xml`, `robots.txt`, and application
  icons touched by the refresh;
- the five retired generators that now fail closed.

The implementation commit is the authoritative inventory. Use `git show
--stat <candidate-sha>` and `git show --name-status <candidate-sha>` rather than
maintaining a hand-written file count during rollback.

## 3. Preferred local rollback

Use non-destructive reverts so the refresh and its rollback remain auditable.
If the branch has an implementation commit followed by an evidence-only commit,
revert newest first:

```powershell
git log --oneline -6
git revert <evidence-commit-sha>
git revert <implementation-commit-sha>
```

Then run the baseline checks appropriate to the restored state. Do not push the
rollback unless a separate instruction authorizes publication.

If the entire feature branch is rejected before publication, the safest action
is to keep the branch and its bundle, switch back to `main`, and leave the
isolated checkout untouched until the operator confirms it can be removed.

## 4. Partial rollback and regeneration

If only one subsystem is defective, revert the commit that owns it or restore
the affected paths from the immediately previous candidate commit. Then rebuild
with the supported pipeline:

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

Both HTML rewriters must converge to zero changes on their second run.

Never run these retired authors; they intentionally fail closed because they
encode the old identity, taxonomy, or URL contract:

- `scripts/build_landing_pages.py`
- `scripts/build_pillar_pages.py`
- `scripts/regen_sitemap.py`
- `scripts/repair_p5_pillar_nav_footer.py`
- `scripts/rewrite_nav_footer.py`

`artifacts/baseline-routes.json` is pinned. Do not regenerate or overwrite it
when evaluating a rollback.

## 5. Future production rollback

This section applies only after an approved release has actually shipped.

Before deploying, the authorized release lane must record:

- the exact candidate Git SHA;
- the new Vercel deployment ID and production aliases;
- the immediately previous healthy Vercel deployment ID and Git SHA;
- live readback for homepage, services, portfolio, sitemap, redirects, forms,
  booking, and chat.

If a material production defect appears, promote the recorded previous healthy
Vercel deployment. Verify the target first; do not rely on an old deployment ID
copied from this document because deployment state can change.

After promotion, verify:

- apex redirects to `www`;
- homepage and representative service/portfolio/article pages return 200;
- canonical and Open Graph URLs use `https://www.revelationagency.com`;
- `robots.txt` and the restored sitemap agree;
- a representative legacy route resolves through one direct redirect;
- the contact form target, footer mini-form line, booking iframe, chat loader,
  mailto, and telephone links match the known-good receipt;
- an unknown path renders the custom 404.

DNS is not the first rollback mechanism. A Vercel deployment promotion is
faster and more reversible; DNS changes require separate explicit authority.

## 6. Protected external state

The refresh does not alter production form endpoints, chat widget IDs, booking
configuration, GHL workflows, analytics destinations, CRM records, email, SMS,
or DNS. A future phase that changes any of those must create its own versioned
rollback receipt before activation.

## 7. Hard safety rules

- Do not force-push `main`.
- Do not rewrite or delete the remote baseline.
- Do not discard the branch or isolated checkout until a verified bundle exists.
- Do not delete the evidence artifacts before the rollback is accepted.
- Do not touch the Command Center, Portal, or other desktop checkouts; they are
  outside this repository boundary.
- Do not use DNS as the first response to an application defect.

## 8. Attestation

No rollback has been executed. No production release exists from this local
candidate. The branch, commits, and evidence packet are the recovery boundary
until a separately authorized deployment records a live release receipt.
