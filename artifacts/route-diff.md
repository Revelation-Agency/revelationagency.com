# Route diff — baseline vs proposed

- Baseline URL count: 122
- Proposed URL count: 121
- Retained (unchanged path): 96
- Retired (redirected via redirect-map.json): 26
- New URLs: 25

Every retired URL has exactly ONE permanent, direct redirect in `redirect-map.json`.
No chains, no loops. Case-study URLs are all retained.

## Retired (301 to new)

- `https://www.revelationagency.com/portfolio/creative.html` → `/portfolio/branding.html`
- `https://www.revelationagency.com/portfolio/creative/app-development.html` → `/portfolio/branding/apps-digital-products.html`
- `https://www.revelationagency.com/portfolio/creative/branding.html` → `/portfolio/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/portfolio/creative/video-production.html` → `/portfolio/branding/video-visual-content.html`
- `https://www.revelationagency.com/portfolio/creative/website-development.html` → `/portfolio/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/portfolio/marketing/digital-ads.html` → `/portfolio/sales/conversion-advertising.html`
- `https://www.revelationagency.com/portfolio/marketing/outsource-marketing.html` → `/portfolio/marketing/`
- `https://www.revelationagency.com/portfolio/marketing/search-rankings.html` → `/portfolio/marketing/seo-ai-visibility.html`
- `https://www.revelationagency.com/portfolio/systems.html` → `/portfolio.html`
- `https://www.revelationagency.com/portfolio/systems/ai-automation.html` → `/portfolio/ai-automation.html`
- `https://www.revelationagency.com/portfolio/systems/brand-systems.html` → `/portfolio/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/portfolio/systems/digital-presence.html` → `/portfolio/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/portfolio/systems/sales-infrastructure.html` → `/portfolio/sales/crm-sales-infrastructure.html`
- `https://www.revelationagency.com/services/creative/` → `/services/branding/`
- `https://www.revelationagency.com/services/creative/app-development.html` → `/services/branding/apps-digital-products.html`
- `https://www.revelationagency.com/services/creative/branding.html` → `/services/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/services/creative/video-production.html` → `/services/branding/video-visual-content.html`
- `https://www.revelationagency.com/services/creative/website-development.html` → `/services/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/services/marketing/digital-ads.html` → `/services/sales/conversion-advertising.html`
- `https://www.revelationagency.com/services/marketing/outsource-marketing.html` → `/services/marketing/`
- `https://www.revelationagency.com/services/marketing/search-rankings.html` → `/services/marketing/seo-ai-visibility.html`
- `https://www.revelationagency.com/services/systems/` → `/services.html`
- `https://www.revelationagency.com/services/systems/ai-automation.html` → `/services/ai-automation.html`
- `https://www.revelationagency.com/services/systems/brand-systems.html` → `/services/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/services/systems/digital-presence.html` → `/services/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/services/systems/sales-infrastructure.html` → `/services/sales/crm-sales-infrastructure.html`

## New URLs

- `https://www.revelationagency.com/portfolio/ai-automation.html`
- `https://www.revelationagency.com/portfolio/branding.html`
- `https://www.revelationagency.com/portfolio/branding/apps-digital-products.html`
- `https://www.revelationagency.com/portfolio/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/portfolio/branding/video-visual-content.html`
- `https://www.revelationagency.com/portfolio/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/portfolio/marketing/`
- `https://www.revelationagency.com/portfolio/marketing/seo-ai-visibility.html`
- `https://www.revelationagency.com/portfolio/sales.html`
- `https://www.revelationagency.com/portfolio/sales/conversion-advertising.html`
- `https://www.revelationagency.com/portfolio/sales/crm-sales-infrastructure.html`
- `https://www.revelationagency.com/services/ai-automation.html`
- `https://www.revelationagency.com/services/branding/`
- `https://www.revelationagency.com/services/branding/apps-digital-products.html`
- `https://www.revelationagency.com/services/branding/brand-strategy-identity.html`
- `https://www.revelationagency.com/services/branding/video-visual-content.html`
- `https://www.revelationagency.com/services/branding/websites-landing-pages.html`
- `https://www.revelationagency.com/services/marketing/email-lifecycle-marketing.html`
- `https://www.revelationagency.com/services/marketing/positioning-content-authority.html`
- `https://www.revelationagency.com/services/marketing/seo-ai-visibility.html`
- `https://www.revelationagency.com/services/sales/`
- `https://www.revelationagency.com/services/sales/conversion-advertising.html`
- `https://www.revelationagency.com/services/sales/crm-sales-infrastructure.html`
- `https://www.revelationagency.com/services/sales/follow-up-nurture.html`
- `https://www.revelationagency.com/services/sales/lead-generation-outreach.html`
