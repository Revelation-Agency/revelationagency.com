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
/sitemap.xml          119 URLs (regenerable)
/robots.txt           production allowlist
/vercel.json          rewrites, security headers, conditional noindex
```

## Indexing behavior

`vercel.json` applies `X-Robots-Tag: noindex, nofollow` to every host **except**
`revelationagency.com` and `www.revelationagency.com`. Production is therefore
indexable; preview deploys and any non-prod host are not.

Internal/template pages (currently none in this repo) can also carry their own
`<meta name="robots" content="noindex,nofollow">` for host-agnostic protection.

## Local preview

Any static HTTP server works:

```bash
python -m http.server 8000
# or
npx serve .
```

## Sitemap regeneration

`scripts/regen_sitemap.py` walks all `.html` files and rewrites `sitemap.xml`
with today's `<lastmod>`. Run after adding or removing pages.

## Deployment

Vercel auto-deploys on push to `main`. The `vercel.json` is the only build
config; there is no framework/buildstep -- pure static.
