# Route diff — baseline vs proposed

- Baseline URL count: 122
- Proposed URL count: 111
- Retained (unchanged path): 95
- Retired (redirected via redirect-map.json): 27
- New URLs: 16

The pinned baseline remains byte-stable; comparison here normalizes Vercel clean URLs.
Every truly retired route has exactly ONE permanent, direct redirect in `redirect-map.json`.
No chains, no loops. Case-study URLs are all retained.

## Retired (301 to new)

- `https://www.revelationagency.com/portfolio/creative` → `/portfolio/branding`
- `https://www.revelationagency.com/portfolio/creative/app-development` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/creative/branding` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/creative/video-production` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/creative/website-development` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/marketing/digital-ads` → `/portfolio/sales?filter=sales`
- `https://www.revelationagency.com/portfolio/marketing/outsource-marketing` → `/portfolio/marketing?filter=marketing`
- `https://www.revelationagency.com/portfolio/marketing/search-rankings` → `/portfolio/marketing?filter=marketing`
- `https://www.revelationagency.com/portfolio/marketing/social-media` → `/portfolio/marketing?filter=marketing`
- `https://www.revelationagency.com/portfolio/systems` → `/portfolio`
- `https://www.revelationagency.com/portfolio/systems/ai-automation` → `/services/ai-automation`
- `https://www.revelationagency.com/portfolio/systems/brand-systems` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/systems/digital-presence` → `/portfolio/branding?filter=branding`
- `https://www.revelationagency.com/portfolio/systems/sales-infrastructure` → `/portfolio/sales?filter=sales`
- `https://www.revelationagency.com/services/creative` → `/services/branding`
- `https://www.revelationagency.com/services/creative/app-development` → `/services/branding/apps-digital-products`
- `https://www.revelationagency.com/services/creative/branding` → `/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/creative/video-production` → `/services/branding/video-visual-content`
- `https://www.revelationagency.com/services/creative/website-development` → `/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/marketing/digital-ads` → `/services/sales/conversion-advertising`
- `https://www.revelationagency.com/services/marketing/outsource-marketing` → `/services/marketing`
- `https://www.revelationagency.com/services/marketing/search-rankings` → `/services/marketing/seo-ai-visibility`
- `https://www.revelationagency.com/services/systems` → `/services`
- `https://www.revelationagency.com/services/systems/ai-automation` → `/services/ai-automation`
- `https://www.revelationagency.com/services/systems/brand-systems` → `/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/systems/digital-presence` → `/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/systems/sales-infrastructure` → `/services/sales/crm-sales-infrastructure`

## New URLs

- `https://www.revelationagency.com/portfolio/branding`
- `https://www.revelationagency.com/portfolio/sales`
- `https://www.revelationagency.com/services/ai-automation`
- `https://www.revelationagency.com/services/branding`
- `https://www.revelationagency.com/services/branding/apps-digital-products`
- `https://www.revelationagency.com/services/branding/brand-strategy-identity`
- `https://www.revelationagency.com/services/branding/video-visual-content`
- `https://www.revelationagency.com/services/branding/websites-landing-pages`
- `https://www.revelationagency.com/services/marketing/email-lifecycle-marketing`
- `https://www.revelationagency.com/services/marketing/positioning-content-authority`
- `https://www.revelationagency.com/services/marketing/seo-ai-visibility`
- `https://www.revelationagency.com/services/sales`
- `https://www.revelationagency.com/services/sales/conversion-advertising`
- `https://www.revelationagency.com/services/sales/crm-sales-infrastructure`
- `https://www.revelationagency.com/services/sales/follow-up-nurture`
- `https://www.revelationagency.com/services/sales/lead-generation-outreach`
