/*
 * Revelation Agency — Website Template Catalog
 * ------------------------------------------------
 * Single source of truth for the /templates.html page.
 * To add a new template:
 *   1. Drop the template files under ../../templates/<family>/...
 *   2. Add a new object to the RA_TEMPLATE_CATALOG array below.
 *   3. Reload templates.html — filters + cards update automatically.
 *
 * Required fields:
 *   id           unique slug (kebab-case)
 *   title        display name shown on the card
 *   family       source family ("Pixora", "Smart", "Template 3")
 *   description  one-sentence positioning line (no pricing)
 *   tier         "Starter" | "Refined" | "Premium"
 *   complexity   "Simple" | "Moderate" | "Advanced"
 *   industry     string[] — must use canonical buckets (see RA_INDUSTRY_TAXONOMY)
 *   style        string[] — descriptive tags (Minimal, Bold, Corporate, etc.)
 *   previewHref  relative link to the template's live preview (index.html)
 *   thumbnail    relative image path used on the card (fallback handled by render layer)
 *
 * Optional fields:
 *   accent       hex color string used for card accent bar
 *   featured     boolean — surfaces card at the top of the grid
 *
 * Canonical Industry taxonomy (16 buckets — keep filter chips usable):
 *   IT & Technology              — IT, SaaS, software, AI, crypto, dev tools
 *   Agency & Studio              — agencies, branding, creative studios
 *   Corporate & Consulting       — B2B services, professional firms, multipurpose business
 *   Hospitality                  — hotels, restaurants, food, travel
 *   Real Estate                  — property listings, brokerages, agents
 *   Health & Fitness             — gyms, fitness, sports clubs, health
 *   Construction & Trades        — contractors, construction, trades
 *   Legal                        — lawyers, legal practices, compliance
 *   Finance                      — finance, loans, banking, investment
 *   Architecture & Interior      — architecture firms, interior design
 *   Retail & E-commerce          — shops, marketplaces, fashion, furniture
 *   Portfolio                    — photographers, portfolio sites, showcase
 *   Personal Brand               — speakers, coaches, lifestyle, personal sites
 *   Outdoor & Agriculture        — landscape, exterior, farms, agriculture
 *   Logistics & Automotive       — delivery, rental, automotive, logistics
 *   Marketing                    — landing pages, campaign sites, lead capture
 *
 * Each entry should carry 1–3 of these. Don't invent new buckets without
 * adding them to the taxonomy comment above first — the filter chips are
 * built dynamically from this field, so spelling drift creates new chips.
 */

window.RA_TEMPLATE_CATALOG = [
	// -----------------------------------------------------------
	// PIXORA FAMILY — modern multi-demo creative / agency theme
	// -----------------------------------------------------------
	{
		id: "pixora-default",
		title: "Pixora — Creative Studio",
		family: "Pixora",
		description: "Bold editorial layouts for creative studios and portfolio-driven brands.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Agency & Studio", "Portfolio"],
		style: ["Bold", "Editorial", "Dark"],
		previewHref: "../../templates/pixora/index.html",
		thumbnail: "../../templates/pixora/assets/img/webgl/3-thumb.webp",
		featured: true
	},
	{
		id: "pixora-ai-startup",
		title: "Pixora — AI Startup",
		family: "Pixora",
		description: "Sharp, high-tech landing experience tuned for AI and SaaS launches.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["IT & Technology"],
		style: ["Tech", "Minimal", "Dark"],
		previewHref: "../../templates/pixora/ai-startup.html",
		thumbnail: "../../templates/pixora/assets/img/webgl/5-thumb.webp"
	},
	{
		id: "pixora-architecture",
		title: "Pixora — Architecture Studio",
		family: "Pixora",
		description: "Slow, cinematic scroll made for architecture and interior firms.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Architecture & Interior", "Agency & Studio"],
		style: ["Cinematic", "Minimal", "Light"],
		previewHref: "../../templates/pixora/architecture.html",
		thumbnail: "../../templates/pixora/assets/img/gellary/04.jpg"
	},
	{
		id: "pixora-branding-agency",
		title: "Pixora — Branding Agency",
		family: "Pixora",
		description: "Premium branding agency layout with portfolio and case-study depth.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Agency & Studio"],
		style: ["Editorial", "Bold"],
		previewHref: "../../templates/pixora/branding-agency.html",
		thumbnail: "../../templates/pixora/assets/img/webgl/2-thumb.webp"
	},
	{
		id: "pixora-parallax-carousel",
		title: "Pixora — Parallax Carousel",
		family: "Pixora",
		description: "Parallax carousel hero for high-impact portfolios and launches.",
		tier: "Refined",
		complexity: "Advanced",
		industry: ["Portfolio", "Agency & Studio"],
		style: ["Motion", "Parallax", "Dark"],
		previewHref: "../../templates/pixora/parallax-carousel.html",
		thumbnail: "../../templates/pixora/assets/img/project/06.jpg"
	},
	{
		id: "pixora-showcase-carousel",
		title: "Pixora — Showcase Carousel",
		family: "Pixora",
		description: "Full-bleed showcase carousel for photographers and product launches.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Portfolio"],
		style: ["Cinematic", "Minimal"],
		previewHref: "../../templates/pixora/showcase-carousel.html",
		thumbnail: "../../templates/pixora/assets/img/parallax-slider/port-8.jpg"
	},

	// -----------------------------------------------------------
	// SMART FAMILY — digital-agency portfolio base theme
	// -----------------------------------------------------------
	{
		id: "smart-digital-agency",
		title: "Smart — Digital Agency",
		family: "Smart",
		description: "Clean digital-agency base with full services, portfolio, and blog suite.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Agency & Studio", "IT & Technology"],
		style: ["Minimal", "Modern", "Light"],
		previewHref: "../../templates/Smart/smart/index.html",
		thumbnail: "../../templates/Smart/smart/assets/img/bg/hero-bg-1.jpg"
	},

	// -----------------------------------------------------------
	// TEMPLATE 3 FAMILY — 28 themed verticals
	// -----------------------------------------------------------
	{
		id: "tpl3-default",
		title: "Modern Business — Default",
		family: "Template 3",
		description: "Neutral business shell ready for any service-led brand.",
		tier: "Starter",
		complexity: "Simple",
		industry: ["Corporate & Consulting"],
		style: ["Minimal", "Corporate"],
		previewHref: "../../templates/Template%203/templates/62267-default/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62267-default/site/images/parallax-01.jpg"
	},
	{
		id: "tpl3-modern-hotel",
		title: "Modern Hotel",
		family: "Template 3",
		description: "Hospitality layout with rooms, amenities, and booking prompts.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Hospitality"],
		style: ["Elegant", "Warm"],
		previewHref: "../../templates/Template%203/templates/62268-modern-hotel/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62268-modern-hotel/site/images/slider-slide-1.jpg"
	},
	{
		id: "tpl3-construction",
		title: "Construction Co.",
		family: "Template 3",
		description: "Construction and contractor layout with projects and service grid.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Construction & Trades"],
		style: ["Industrial", "Bold"],
		previewHref: "../../templates/Template%203/templates/62269-construction/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62269-construction/site/images/slider-slide-1-1920x1080.jpg"
	},
	{
		id: "tpl3-corporate",
		title: "Corporate",
		family: "Template 3",
		description: "Structured corporate layout for finance, consulting, and B2B firms.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Corporate & Consulting", "Finance"],
		style: ["Corporate", "Clean"],
		previewHref: "../../templates/Template%203/templates/62270-corporate/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62270-corporate/site/images/bg-image-1920x683.jpg"
	},
	{
		id: "tpl3-fitness",
		title: "Fitness",
		family: "Template 3",
		description: "High-energy fitness layout with classes, trainers, and pricing blocks.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Health & Fitness"],
		style: ["Bold", "Energetic"],
		previewHref: "../../templates/Template%203/templates/62271-fitness/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62271-fitness/site/images/home-11.jpg"
	},
	{
		id: "tpl3-furni",
		title: "Furni — Furniture Store",
		family: "Template 3",
		description: "Furniture and home-goods layout with product grid and category nav.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Retail & E-commerce"],
		style: ["Minimal", "Warm"],
		previewHref: "../../templates/Template%203/templates/62272-furni/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62272-furni/site/images/banner-1-573x914.jpg"
	},
	{
		id: "tpl3-fashion-blog",
		title: "Fashion Blog",
		family: "Template 3",
		description: "Editorial fashion blog with long-read posts and lookbook grid.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Retail & E-commerce", "Personal Brand"],
		style: ["Editorial", "Light"],
		previewHref: "../../templates/Template%203/templates/62273-fashion-blog/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62273-fashion-blog/site/images/slider-slide-13-1920x1080.jpg"
	},
	{
		id: "tpl3-lawyer",
		title: "Lawyer / Legal",
		family: "Template 3",
		description: "Trust-forward legal layout with practice areas and attorney bios.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Legal"],
		style: ["Corporate", "Serious"],
		previewHref: "../../templates/Template%203/templates/62274-lawyer/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62274-lawyer/site/images/parallax-1.jpg"
	},
	{
		id: "tpl3-loan-offer",
		title: "Loan Offer",
		family: "Template 3",
		description: "Finance / loan landing with calculator and lead-capture flow.",
		tier: "Starter",
		complexity: "Simple",
		industry: ["Finance"],
		style: ["Corporate", "Clean"],
		previewHref: "../../templates/Template%203/templates/62275-loan-offer/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62275-loan-offer/site/images/home-parallax-01.jpg"
	},
	{
		id: "tpl3-resto",
		title: "Resto — Restaurant",
		family: "Template 3",
		description: "Restaurant layout with menu, reservations, and gallery.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Hospitality"],
		style: ["Warm", "Elegant"],
		previewHref: "../../templates/Template%203/templates/62276-resto/site/index.html",
		thumbnail: "../../templates/Template%203/templates/62276-resto/site/images/index-1-1920x1080.jpg"
	},
	{
		id: "tpl3-landing",
		title: "Landing Base",
		family: "Template 3",
		description: "Clean one-page landing base for quick campaign rollouts.",
		tier: "Starter",
		complexity: "Simple",
		industry: ["Marketing"],
		style: ["Minimal"],
		previewHref: "../../templates/Template%203/templates/landing/site/index.html",
		thumbnail: "../../templates/Template%203/templates/landing/site/images/home-00.jpg"
	},
	{
		id: "tpl3-interior",
		title: "Interior Design",
		family: "Template 3",
		description: "Interior design portfolio with project gallery and lookbook.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Architecture & Interior"],
		style: ["Minimal", "Elegant"],
		previewHref: "../../templates/Template%203/templates/prod-13716-interior/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-13716-interior/site/images/bg-image-1.jpg"
	},
	{
		id: "tpl3-construction-v2",
		title: "Construction — Projects",
		family: "Template 3",
		description: "Alt construction theme focused on project history and service lines.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Construction & Trades"],
		style: ["Industrial"],
		previewHref: "../../templates/Template%203/templates/prod-13732-construction/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-13732-construction/site/images/slider-slide-1-1920x1080-thumb.webp"
	},
	{
		id: "tpl3-business",
		title: "Business Pro",
		family: "Template 3",
		description: "Multipurpose business layout with services, team, and contact flow.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Corporate & Consulting"],
		style: ["Corporate", "Clean"],
		previewHref: "../../templates/Template%203/templates/prod-13850-business/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-13850-business/site/images/parallax-1.jpg"
	},
	{
		id: "tpl3-real-estate",
		title: "Real Estate",
		family: "Template 3",
		description: "Listings, agent profiles, and neighborhood sections for property brands.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Real Estate"],
		style: ["Elegant", "Corporate"],
		previewHref: "../../templates/Template%203/templates/prod-15821-real-estate/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-15821-real-estate/site/images/slider-slide-1.jpg"
	},
	{
		id: "tpl3-extrafast",
		title: "ExtraFast — Delivery",
		family: "Template 3",
		description: "Logistics and fast-delivery landing with tracking and service CTAs.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Logistics & Automotive"],
		style: ["Bold", "Energetic"],
		previewHref: "../../templates/Template%203/templates/prod-18905-extrafast/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-18905-extrafast/site/images/slider-slide-1-1920x1080.jpg"
	},
	{
		id: "tpl3-buy-sell",
		title: "Buy & Sell Marketplace",
		family: "Template 3",
		description: "Classifieds marketplace layout with categories and listings.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Retail & E-commerce"],
		style: ["Corporate", "Dense"],
		previewHref: "../../templates/Template%203/templates/prod-18906-buy&sell/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-18906-buy&sell/site/images/bg-image-2-thumb.webp"
	},
	{
		id: "tpl3-fitness-club",
		title: "Fitness Club",
		family: "Template 3",
		description: "Dedicated gym club layout with class schedule and memberships.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Health & Fitness"],
		style: ["Bold", "Energetic"],
		previewHref: "../../templates/Template%203/templates/prod-20815-fitness-club/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-20815-fitness-club/site/images/slide-preivew-2.jpg"
	},
	{
		id: "tpl3-architecture",
		title: "Architecture",
		family: "Template 3",
		description: "Architectural firm layout with project portfolio and team bios.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Architecture & Interior"],
		style: ["Minimal", "Elegant"],
		previewHref: "../../templates/Template%203/templates/prod-20819-architecture/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-20819-architecture/site/images/slide-1-1339x729.jpg"
	},
	{
		id: "tpl3-interior-v2",
		title: "Interior — Studio",
		family: "Template 3",
		description: "Alt interior studio theme with softer palette and lookbook focus.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Architecture & Interior"],
		style: ["Warm", "Elegant"],
		previewHref: "../../templates/Template%203/templates/prod-20821-interior/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-20821-interior/site/images/home-02-370x222.jpg"
	},
	{
		id: "tpl3-one-service",
		title: "One Service",
		family: "Template 3",
		description: "Single-service landing page, tight focus, fast to ship.",
		tier: "Starter",
		complexity: "Simple",
		industry: ["Marketing", "Corporate & Consulting"],
		style: ["Minimal", "Clean"],
		previewHref: "../../templates/Template%203/templates/prod-20823-one-service/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-20823-one-service/site/images/slider-01-671x671.png"
	},
	{
		id: "tpl3-ico",
		title: "ICO / Crypto",
		family: "Template 3",
		description: "ICO and crypto launch landing with roadmap and tokenomics blocks.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["IT & Technology", "Finance"],
		style: ["Tech", "Bold", "Dark"],
		previewHref: "../../templates/Template%203/templates/prod-21466-ico/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-21466-ico/site/images/image-1-715x521.png"
	},
	{
		id: "tpl3-motivation-speakers",
		title: "Motivational Speaker",
		family: "Template 3",
		description: "Personal brand site for speakers, coaches, and event personalities.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Personal Brand"],
		style: ["Bold", "Editorial"],
		previewHref: "../../templates/Template%203/templates/prod-23871-motivation-speakers/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-23871-motivation-speakers/site/images/home-01-613x701.jpg"
	},
	{
		id: "tpl3-exterior-design",
		title: "Exterior Design",
		family: "Template 3",
		description: "Landscape and exterior design portfolio with project highlights.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Outdoor & Agriculture", "Architecture & Interior"],
		style: ["Natural", "Warm"],
		previewHref: "../../templates/Template%203/templates/prod-31157-exterior-design/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-31157-exterior-design/site/images/home-08-1920x800.jpg"
	},
	{
		id: "tpl3-farm",
		title: "Farm / Agriculture",
		family: "Template 3",
		description: "Farm and agriculture landing with products and story sections.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Outdoor & Agriculture"],
		style: ["Natural", "Warm"],
		previewHref: "../../templates/Template%203/templates/prod-31368-farm/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-31368-farm/site/images/index-01-560x700.jpg"
	},
	{
		id: "tpl3-badminton",
		title: "Badminton Club",
		family: "Template 3",
		description: "Sports club layout with events, coaches, and membership tiers.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Health & Fitness"],
		style: ["Energetic", "Bold"],
		previewHref: "../../templates/Template%203/templates/prod-31589-badminton/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-31589-badminton/site/images/home-02-400x505.jpg"
	},
	{
		id: "tpl3-hotel",
		title: "Boutique Hotel",
		family: "Template 3",
		description: "Boutique hotel site with rooms, dining, and booking flow.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Hospitality"],
		style: ["Elegant", "Warm"],
		previewHref: "../../templates/Template%203/templates/prod-33047-hotel/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-33047-hotel/site/images/home-01-1200x800.jpg"
	},
	{
		id: "tpl3-car-rental",
		title: "Car Rental",
		family: "Template 3",
		description: "Fleet listing, rental flow, and driver policies for car-rental brands.",
		tier: "Premium",
		complexity: "Advanced",
		industry: ["Logistics & Automotive"],
		style: ["Bold", "Clean"],
		previewHref: "../../templates/Template%203/templates/prod-33207-car-rental/site/index.html",
		thumbnail: "../../templates/Template%203/templates/prod-33207-car-rental/site/images/parallax-01.jpg"
	},

	// -----------------------------------------------------------
	// FLEX IT FAMILY — IT solutions / business services multi-demo
	// Two curated entries from the 6-variant bundle:
	//   • Slider Showcase (default) — cinematic 3-frame slider hero
	//   • Video Hero — full-bleed background-video hero
	// -----------------------------------------------------------
	{
		id: "flex-it-slider-showcase",
		title: "Flex IT — Slider Showcase",
		family: "Flex IT",
		description: "Cinematic 3-frame slider hero, full IT-solutions surface, ships inside a 6-variant homepage bundle.",
		tier: "Refined",
		complexity: "Advanced",
		industry: ["IT & Technology", "Corporate & Consulting"],
		style: ["Modern", "Corporate", "Bold"],
		previewHref: "../../templates/flex-it-html5-website-template/html/index.html",
		thumbnail: "../../templates/flex-it-html5-website-template/html/assets/images/hero/hero-bg-1.jpg"
	},
	{
		id: "flex-it-video-hero",
		title: "Flex IT — Video Hero",
		family: "Flex IT",
		description: "Full-bleed background-video hero variant from the Flex IT bundle, tuned for high-impact tech and IT launches.",
		tier: "Refined",
		complexity: "Advanced",
		industry: ["IT & Technology", "Corporate & Consulting"],
		style: ["Modern", "Bold", "Motion"],
		previewHref: "../../templates/flex-it-html5-website-template/html/home-6.html",
		thumbnail: "../../templates/flex-it-html5-website-template/html/assets/images/hero/hero-bg-2-thumb.webp"
	},

	// -----------------------------------------------------------
	// INDISOFT FAMILY — IT technology / software services
	// -----------------------------------------------------------
	{
		id: "indisoft-it-technology",
		title: "Indisoft — IT Technology",
		family: "Indisoft",
		description: "Multi-page IT technology template with services, projects, packages, blog, and auth surfaces.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["IT & Technology"],
		style: ["Modern", "Corporate", "Clean"],
		previewHref: "../../templates/Indisoft%20v2/Indisoft-%20It%20Technology%20Website%20Template/index.html",
		thumbnail: "../../templates/Indisoft%20v2/Indisoft-%20It%20Technology%20Website%20Template/assets/images/hero-bg.jpg"
	},

	// -----------------------------------------------------------
	// DELEX FAMILY — corporate business
	// -----------------------------------------------------------
	{
		id: "delex-corporate-business",
		title: "Delex — Corporate Business",
		family: "Delex",
		description: "Trust-forward corporate business layout with services, features, team, pricing, and lead-capture flow.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["Corporate & Consulting"],
		style: ["Corporate", "Clean", "Professional"],
		previewHref: "../../templates/Delex-HTML-Main-Files/HTML/index.html",
		thumbnail: "../../templates/Delex-HTML-Main-Files/HTML/assets/images/carousel-1-thumb.webp"
	},

	// -----------------------------------------------------------
	// TECHIDA FAMILY — IT solutions multi-demo
	// One curated entry pointed at the magazine-grid hero (index-3),
	// the strongest of the three shipped homepage variants.
	// -----------------------------------------------------------
	{
		id: "techida-it-solutions",
		title: "Techida — IT Solutions",
		family: "Techida",
		description: "Magazine-grid hero with stat counters, three homepage variants in the bundle, and full portfolio, services, and blog surfaces.",
		tier: "Refined",
		complexity: "Moderate",
		industry: ["IT & Technology", "Corporate & Consulting"],
		style: ["Tech", "Modern", "Editorial"],
		previewHref: "../../templates/techida/techida/index-3.html",
		thumbnail: "../../templates/techida/techida/images/hero/2-thumb.webp"
	},

	// -----------------------------------------------------------
	// JALIL FAMILY — personal portfolio landing
	// -----------------------------------------------------------
	{
		id: "jalil-personal-portfolio",
		title: "Jalil — Personal Portfolio",
		family: "Jalil",
		description: "Single-page personal portfolio landing with a simple conversion-focused structure.",
		tier: "Starter",
		complexity: "Simple",
		industry: ["Personal Brand", "Portfolio"],
		style: ["Minimal", "Personal", "Clean"],
		previewHref: "../../templates/jalil/HTML/index.html",
		thumbnail: "../../templates/jalil/HTML/images/banner.jpg"
	}
];
