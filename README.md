# revelationagency.com

Production static site for Revelation Agency.

Deployed via Vercel from the `main` branch.

## Structure

```
/                     index.html + top-level pages
/assets/              CSS, JS, fonts, images, logos
/portfolio/           portfolio hubs + case-study pages
/services/            service hubs + leaf pages
/the-reveal/          articles
/sales-intelligence/  Sales Intelligence capability page
/sitemap.xml          111 clean canonical URLs (regenerable)
/robots.txt           production allowlist
/vercel.json          rewrites, security headers, conditional noindex
```

## Indexing behavior

`vercel.json` applies `X-Robots-Tag: noindex, nofollow` to every host **except**
`revelationagency.com` and `www.revelationagency.com`. Production is therefore
indexable; preview deploys and any non-prod host are not.

Internal/template pages, including `the-reveal/article-template.html`, carry
their own `<meta name="robots" content="noindex,nofollow">` for host-agnostic
protection and are excluded from the sitemap.

## Local preview

Any static HTTP server works:

```bash
python -m http.server 8000
# or
npx serve .
```

## Sitemap regeneration

The canonical route inventory owns both routing and the sitemap. After adding or
removing pages, run:

```bash
python scripts/build_routes_artifacts.py
python scripts/write_vercel_and_sitemap.py
python scripts/verify_2026_refresh.py --max-errors 0
```

The retired `scripts/regen_sitemap.py` command fails closed because it emitted
legacy `.html` URLs, the apex host, and redirect-only pages.

## 2026 refresh maintenance

The supported deterministic pipeline is:

```bash
python scripts/build_2026_brand_assets.py
python scripts/apply_2026_site_refresh.py
python scripts/apply_2026_portfolio_taxonomy.py
python scripts/build_routes_artifacts.py
python scripts/write_vercel_and_sitemap.py
python scripts/verify_integration_preservation.py
python scripts/verify_2026_refresh.py --max-errors 0
python scripts/run_tests.py
```

The current RA identity lives in `assets/brand/current/`. The six first-party
editorial visuals, generation prompts, usage notes, and SHA-256 hashes live in
`assets/brand/visuals/2026/`. Portfolio category membership is owned by
`assets/data/portfolio-taxonomy-2026.json`; do not hand-edit generated pillar
shelves.

Both HTML rewriters are idempotent and must report zero changed files on a
second run. Superseded page authors fail closed so they cannot restore the old
identity, Systems / Creative taxonomy, or `.html` URL contract.

## Deployment

Vercel auto-deploys on push to `main`. The `vercel.json` is the only build
config; there is no framework/buildstep -- pure static.
