/*
 * Revelation Agency — Templates Catalog Render Layer
 * ---------------------------------------------------
 * Reads window.RA_TEMPLATE_CATALOG from templates-catalog.js and:
 *   - Builds the Industry filter chips dynamically from unique industry tags
 *   - Renders the card grid into #templates-grid
 *   - Wires up chip click handlers that stack industry + tier + complexity
 *   - Updates the #templates-count and toggles the empty state
 *
 * All filters are additive within their own group (pick one of N) but independent
 * across groups. "All" in a group clears that group's filter.
 */

(function () {
	"use strict";

	const STATE = {
		industry: "all",
		tier: "all",
		complexity: "all",
		q: ""
	};

	// -------------------------------------------------------------
	// URL hash state — lets filtered views be shared as a link.
	// Format: #industry=Agency&tier=Premium&complexity=Advanced&q=ai
	// -------------------------------------------------------------
	function readHashState() {
		const hash = (window.location.hash || "").replace(/^#/, "");
		if (!hash) return;
		hash.split("&").forEach(function (pair) {
			if (!pair) return;
			const idx = pair.indexOf("=");
			if (idx < 0) return;
			const key = decodeURIComponent(pair.slice(0, idx));
			const val = decodeURIComponent(pair.slice(idx + 1));
			if (key in STATE) STATE[key] = val;
		});
	}

	function writeHashState() {
		const parts = [];
		if (STATE.industry && STATE.industry !== "all") parts.push("industry=" + encodeURIComponent(STATE.industry));
		if (STATE.tier && STATE.tier !== "all") parts.push("tier=" + encodeURIComponent(STATE.tier));
		if (STATE.complexity && STATE.complexity !== "all") parts.push("complexity=" + encodeURIComponent(STATE.complexity));
		if (STATE.q) parts.push("q=" + encodeURIComponent(STATE.q));
		const next = parts.length ? "#" + parts.join("&") : "";
		// Avoid scroll jumps by using replaceState when available.
		if (window.history && window.history.replaceState) {
			const url = window.location.pathname + window.location.search + next;
			window.history.replaceState(null, "", url);
		} else {
			window.location.hash = next;
		}
	}

	function byText(a, b) {
		return a.localeCompare(b);
	}

	function unique(list) {
		return Array.from(new Set(list));
	}

	function escapeHtml(str) {
		if (str == null) return "";
		return String(str)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;");
	}

	function buildIndustryChips(catalog) {
		const group = document.querySelector('[data-filter-group="industry"]');
		if (!group) return;

		// Count occurrences so we can order chips by template volume (most → least),
		// then alphabetical as a stable tiebreaker. Buckets with the most templates
		// surface first — easier scanning for the most common builds.
		const counts = {};
		catalog.forEach(function (t) {
			(t.industry || []).forEach(function (i) {
				counts[i] = (counts[i] || 0) + 1;
			});
		});
		const industries = Object.keys(counts).sort(function (a, b) {
			if (counts[b] !== counts[a]) return counts[b] - counts[a];
			return a.localeCompare(b);
		});

		// Leave the existing "All" chip in place and append the rest.
		industries.forEach(function (industry) {
			const btn = document.createElement("button");
			btn.type = "button";
			btn.className = "templates-chip";
			btn.setAttribute("data-filter-value", industry);
			btn.textContent = industry + " (" + counts[industry] + ")";
			group.appendChild(btn);
		});
	}

	// Pull a clean display label from the title for the no-image fallback
	// — drops the family prefix so the headline reads naturally inside the
	// thumb tile (e.g. "Pixora — Creative Studio" → "Creative Studio").
	function noImageLabel(item) {
		const title = item.title || "";
		const dashIdx = title.indexOf("—");
		if (dashIdx > -1) return title.slice(dashIdx + 1).trim();
		return title;
	}

	function cardTemplate(item) {
		const title = escapeHtml(item.title);
		const family = escapeHtml(item.family);
		const description = escapeHtml(item.description);
		const tier = escapeHtml(item.tier);
		const complexity = escapeHtml(item.complexity);
		const href = item.previewHref || "#";
		const industries = (item.industry || []).slice(0, 3)
			.map(function (i) { return '<span class="templates-tag">' + escapeHtml(i) + "</span>"; })
			.join("");
		const featured = item.featured ? '<span class="templates-card-featured">Featured</span>' : "";

		// Thumbnail handling.
		// - With image: standard <img> with onerror fallback to the no-image state.
		// - Without image: pre-apply the noimg class and render a clean title tag
		//   so empty cards still feel curated, not broken.
		let thumbClass = "templates-card-thumb";
		let thumbInner;
		if (item.thumbnail) {
			thumbInner = '<img src="' + escapeHtml(item.thumbnail) + '" alt="' + title + ' preview" loading="lazy" onerror="this.parentElement.classList.add(\'templates-card-noimg\'); this.remove();">';
		} else {
			thumbClass = "templates-card-thumb templates-card-noimg";
			thumbInner = '<span class="templates-card-noimg-tag">' + escapeHtml(noImageLabel(item)) + '</span>';
		}

		const searchBlob = [
			item.title,
			item.family,
			item.description,
			(item.industry || []).join(" "),
			(item.style || []).join(" "),
			item.tier,
			item.complexity
		].filter(Boolean).join(" ");

		return (
			'<div class="templates-card-col"' +
				' data-industry="' + escapeHtml((item.industry || []).join("|")) + '"' +
				' data-tier="' + tier + '"' +
				' data-complexity="' + complexity + '"' +
				' data-search="' + escapeHtml(searchBlob) + '">' +
				'<article class="templates-card">' +
					'<div class="' + thumbClass + '">' +
						thumbInner +
						featured +
						'<span class="templates-card-family">' + family + "</span>" +
					"</div>" +
					'<div class="templates-card-body">' +
						'<div class="templates-card-meta">' +
							'<span class="templates-card-tier templates-card-tier-' + tier.toLowerCase() + '">' + tier + "</span>" +
							'<span class="templates-card-complexity">' + complexity + "</span>" +
						"</div>" +
						'<h3 class="templates-card-title">' + title + "</h3>" +
						'<p class="templates-card-desc">' + description + "</p>" +
						'<div class="templates-card-tags">' + industries + "</div>" +
						'<div class="templates-card-actions">' +
							'<a class="atf-themes-btn atf-themes-btn-sm" href="' + escapeHtml(href) + '" target="_blank" rel="noopener">' +
								'<i class="fa-light fa-arrow-up-right-from-square me-2"></i>Preview' +
							"</a>" +
							'<a class="templates-card-link" href="contact.html">' +
								'Start a project <i class="fa-light fa-arrow-right ms-1"></i>' +
							"</a>" +
						"</div>" +
					"</div>" +
				"</article>" +
			"</div>"
		);
	}

	// Tier ordering — Premium first so the strongest scaffolds anchor the grid,
	// then Refined, then Starter. Anything unrecognized falls to the end.
	const TIER_ORDER = { Premium: 0, Refined: 1, Starter: 2 };
	function tierRank(t) {
		return TIER_ORDER[t] != null ? TIER_ORDER[t] : 99;
	}

	function renderGrid(catalog) {
		const grid = document.getElementById("templates-grid");
		if (!grid) return;

		// 1. Featured cards first (curated picks).
		// 2. Then by tier (Premium → Refined → Starter).
		// 3. Then by family alphabetical (stable family clustering).
		// 4. Then by title alphabetical.
		const sorted = catalog.slice().sort(function (a, b) {
			const featuredCmp = (!!b.featured) - (!!a.featured);
			if (featuredCmp !== 0) return featuredCmp;
			const tierCmp = tierRank(a.tier) - tierRank(b.tier);
			if (tierCmp !== 0) return tierCmp;
			const famCmp = (a.family || "").localeCompare(b.family || "");
			if (famCmp !== 0) return famCmp;
			return (a.title || "").localeCompare(b.title || "");
		});

		grid.innerHTML = sorted.map(cardTemplate).join("");
	}

	function cardMatches(card) {
		if (STATE.industry !== "all") {
			const industries = (card.getAttribute("data-industry") || "").split("|");
			if (industries.indexOf(STATE.industry) === -1) return false;
		}
		if (STATE.tier !== "all") {
			if (card.getAttribute("data-tier") !== STATE.tier) return false;
		}
		if (STATE.complexity !== "all") {
			if (card.getAttribute("data-complexity") !== STATE.complexity) return false;
		}
		if (STATE.q) {
			const haystack = (card.getAttribute("data-search") || "").toLowerCase();
			if (haystack.indexOf(STATE.q.toLowerCase()) === -1) return false;
		}
		return true;
	}

	// Count how many filter groups are currently narrowing the catalog.
	// Drives the Reset button badge + the "is anything active?" dim state.
	function activeFilterCount() {
		let n = 0;
		if (STATE.industry && STATE.industry !== "all") n += 1;
		if (STATE.tier && STATE.tier !== "all") n += 1;
		if (STATE.complexity && STATE.complexity !== "all") n += 1;
		if (STATE.q) n += 1;
		return n;
	}

	function syncResetButton() {
		const btn = document.getElementById("templates-reset");
		if (!btn) return;
		const n = activeFilterCount();
		btn.classList.toggle("is-active", n > 0);
		// Rebuild the label so the count reflects current state.
		// Font Awesome icon + "Reset" + optional "(n)" pill.
		btn.innerHTML = '<i class="fa-light fa-xmark me-1"></i>Reset' +
			(n > 0 ? ' <span class="templates-reset-count">' + n + '</span>' : "");
		btn.setAttribute("aria-label",
			n > 0 ? ("Reset all filters (" + n + " active)") : "Reset all filters");
	}

	function applyFilters() {
		const cards = document.querySelectorAll(".templates-card-col");
		let visible = 0;
		cards.forEach(function (card) {
			if (cardMatches(card)) {
				card.style.display = "";
				visible += 1;
			} else {
				card.style.display = "none";
			}
		});

		const countEl = document.getElementById("templates-count");
		if (countEl) {
			countEl.textContent = visible + (visible === 1 ? " template" : " templates");
		}

		const emptyEl = document.getElementById("templates-empty");
		if (emptyEl) {
			emptyEl.style.display = visible === 0 ? "flex" : "none";
		}

		syncResetButton();
	}

	function syncChipUIFromState(groupEl) {
		const groupName = groupEl.getAttribute("data-filter-group");
		if (!groupName || !(groupName in STATE)) return;
		const active = STATE[groupName] || "all";
		groupEl.querySelectorAll(".templates-chip").forEach(function (chip) {
			chip.classList.toggle("active", (chip.getAttribute("data-filter-value") || "all") === active);
		});
	}

	function wireChipGroup(groupEl) {
		const groupName = groupEl.getAttribute("data-filter-group");
		if (!groupName) return;

		groupEl.addEventListener("click", function (event) {
			const btn = event.target.closest(".templates-chip");
			if (!btn) return;

			const value = btn.getAttribute("data-filter-value") || "all";
			STATE[groupName] = value;

			groupEl.querySelectorAll(".templates-chip").forEach(function (chip) {
				chip.classList.toggle("active", chip === btn);
			});

			writeHashState();
			applyFilters();
		});
	}

	function wireSearchInput() {
		const input = document.getElementById("templates-search");
		if (!input) return;

		// Restore value from URL state.
		if (STATE.q) input.value = STATE.q;

		let debounce = null;
		input.addEventListener("input", function () {
			STATE.q = input.value || "";
			clearTimeout(debounce);
			debounce = setTimeout(function () {
				writeHashState();
				applyFilters();
			}, 80);
		});

		// Escape clears the search quickly.
		input.addEventListener("keydown", function (event) {
			if (event.key === "Escape" && input.value) {
				input.value = "";
				STATE.q = "";
				writeHashState();
				applyFilters();
			}
		});
	}

	function resetAllFilters() {
		STATE.industry = "all";
		STATE.tier = "all";
		STATE.complexity = "all";
		STATE.q = "";

		const input = document.getElementById("templates-search");
		if (input) input.value = "";

		document.querySelectorAll("[data-filter-group]").forEach(syncChipUIFromState);

		writeHashState();
		applyFilters();
	}

	function wireResetButton() {
		const btn = document.getElementById("templates-reset");
		if (btn) btn.addEventListener("click", resetAllFilters);

		// Second reset target: the "Clear all filters" button inside the
		// empty state. Same handler, different surface — users hit whichever
		// is closer to where their attention already is.
		const emptyBtn = document.getElementById("templates-empty-reset");
		if (emptyBtn) emptyBtn.addEventListener("click", resetAllFilters);
	}

	// Global "/" shortcut to jump to the search input — matches the pattern
	// every dev tool and modern catalog already uses, so muscle memory wins.
	// We ignore the key when the user is already typing in another field.
	function wireSearchShortcut() {
		const input = document.getElementById("templates-search");
		if (!input) return;

		document.addEventListener("keydown", function (event) {
			if (event.key !== "/") return;
			const target = event.target;
			const tag = (target && target.tagName) || "";
			if (tag === "INPUT" || tag === "TEXTAREA" || (target && target.isContentEditable)) return;
			event.preventDefault();
			input.focus();
			input.select();
		});
	}

	function init() {
		const catalog = window.RA_TEMPLATE_CATALOG || [];
		if (!catalog.length) return;

		readHashState();

		buildIndustryChips(catalog);
		renderGrid(catalog);

		document.querySelectorAll("[data-filter-group]").forEach(function (groupEl) {
			wireChipGroup(groupEl);
			syncChipUIFromState(groupEl);
		});

		wireSearchInput();
		wireResetButton();
		wireSearchShortcut();

		applyFilters();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
