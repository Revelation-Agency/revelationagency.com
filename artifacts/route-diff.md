# Route diff — baseline vs proposed

- Baseline URL count: 122
- Proposed URL count: 112
- Retained (unchanged path): 96
- Retired (redirected via redirect-map.json): 26
- New URLs: 16

The pinned baseline remains byte-stable; comparison here normalizes Vercel clean URLs.
Every truly retired route has exactly ONE permanent, direct redirect in `redirect-map.json`.
No chains, no loops. Case-study URLs are all retained.

## Retired (permanent redirect to successor)

- `https://www.revelationagency.com/portfolio/creative` → `/portfolio/branding`
- `https://www.revelationagency.com/portfolio/creative/app-development` → `/portfolio?filter=b2`
- `https://www.revelationagency.com/portfolio/creative/branding` → `/portfolio?filter=b3`
- `https://www.revelationagency.com/portfolio/creative/video-production` → `/portfolio?filter=b5`
- `https://www.revelationagency.com/portfolio/creative/website-development` → `/portfolio?filter=b1`
- `https://www.revelationagency.com/portfolio/marketing/digital-ads` → `/portfolio?filter=m3`
- `https://www.revelationagency.com/portfolio/marketing/outsource-marketing` → `/portfolio?filter=marketing`
- `https://www.revelationagency.com/portfolio/marketing/search-rankings` → `/portfolio?filter=m1`
- `https://www.revelationagency.com/portfolio/marketing/social-media` → `/portfolio?filter=m2`
- `https://www.revelationagency.com/portfolio/systems` → `/portfolio`
- `https://www.revelationagency.com/portfolio/systems/ai-automation` → `/portfolio?filter=s4`
- `https://www.revelationagency.com/portfolio/systems/brand-systems` → `/portfolio?filter=b3`
- `https://www.revelationagency.com/portfolio/systems/digital-presence` → `/portfolio?filter=b1`
- `https://www.revelationagency.com/portfolio/systems/sales-infrastructure` → `/portfolio?filter=s3`
- `https://www.revelationagency.com/services/creative` → `/services/branding`
- `https://www.revelationagency.com/services/creative/app-development` → `/services/branding/apps-digital-products`
- `https://www.revelationagency.com/services/creative/branding` → `/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/creative/video-production` → `/services/branding/video-visual-content`
- `https://www.revelationagency.com/services/creative/website-development` → `/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/marketing/outsource-marketing` → `/services/marketing`
- `https://www.revelationagency.com/services/marketing/search-rankings` → `/services/marketing/seo-ai-visibility`
- `https://www.revelationagency.com/services/systems` → `/services`
- `https://www.revelationagency.com/services/systems/ai-automation` → `/services/sales/ai-automation-systems`
- `https://www.revelationagency.com/services/systems/brand-systems` → `/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/systems/digital-presence` → `/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/systems/sales-infrastructure` → `/services/sales/crm-sales-infrastructure`

## Post-baseline canonical routes now redirected

- `https://www.revelationagency.com/services/marketing/positioning-content-authority` → `/services/marketing/seo-ai-visibility`
- `https://www.revelationagency.com/services/sales/follow-up-nurture` → `/services/marketing/email-lifecycle-marketing`
- `https://www.revelationagency.com/services/sales/conversion-advertising` → `/services/marketing/digital-ads`
- `https://www.revelationagency.com/services/ai-automation` → `/services/sales/ai-automation-systems`

## New URLs

- `https://www.revelationagency.com/portfolio/branding`
- `https://www.revelationagency.com/portfolio/sales`
- `https://www.revelationagency.com/privacy`
- `https://www.revelationagency.com/services/branding`
- `https://www.revelationagency.com/services/branding/apps-digital-products`
- `https://www.revelationagency.com/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/branding/design`
- `https://www.revelationagency.com/services/branding/video-visual-content`
- `https://www.revelationagency.com/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/marketing/email-lifecycle-marketing`
- `https://www.revelationagency.com/services/marketing/seo-ai-visibility`
- `https://www.revelationagency.com/services/sales`
- `https://www.revelationagency.com/services/sales/ai-automation-systems`
- `https://www.revelationagency.com/services/sales/crm-sales-infrastructure`
- `https://www.revelationagency.com/services/sales/lead-gen-ads`
- `https://www.revelationagency.com/services/sales/lead-generation-outreach`
