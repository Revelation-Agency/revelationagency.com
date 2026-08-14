"""Local desktop + mobile screenshot packet for the P5 rebrand.

Serves the checkout on 127.0.0.1 (no public exposure) and renders the
representative surfaces listed in the packet at 1440x900 (desktop) and
390x844 (mobile). Every rendered image is written under
artifacts/screenshots/{desktop,mobile}/.

Uses fictional / on-site content only — no private dashboards, no client
data, no unapproved metric copy. If Chromium cannot launch the run exits
non-zero so the operator sees the gap.
"""
import http.server
import os
import socket
import sys
import threading
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAGES = [
    ("home",                    "/index.html"),
    ("branding_hub",            "/services/branding/index.html"),
    ("marketing_hub",           "/services/marketing/index.html"),
    ("sales_hub",               "/services/sales/index.html"),
    ("service_leaf_brand_id",   "/services/branding/brand-strategy-identity.html"),
    ("service_leaf_seo",        "/services/marketing/seo-ai-visibility.html"),
    ("service_leaf_crm",        "/services/sales/crm-sales-infrastructure.html"),
    ("ai_crosscut",             "/services/ai-automation.html"),
    ("portfolio_hub",           "/portfolio.html"),
    ("portfolio_branding",      "/portfolio/branding.html"),
    ("case_study_risen_sun",    "/portfolio/case-studies/risen-sun-solar-roofing.html"),
    ("case_study_trust_energy", "/portfolio/case-studies/trust-energy.html"),
    ("reveal_index",            "/the-reveal/index.html"),
    ("about",                   "/about.html"),
    ("contact",                 "/contact.html"),
    ("services_hub",            "/services.html"),
    ("_404",                    "/404.html"),
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_a, **_kw):
        pass


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server():
    port = free_port()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.5)
            break
        except Exception:
            time.sleep(0.1)
    return httpd, port


def main() -> int:
    from playwright.sync_api import sync_playwright  # noqa

    os.makedirs("artifacts/screenshots/desktop", exist_ok=True)
    os.makedirs("artifacts/screenshots/mobile", exist_ok=True)

    httpd, port = start_server()
    base = f"http://127.0.0.1:{port}"
    print(f"local server on {base}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            # Desktop pass
            ctx_d = browser.new_context(viewport={"width": 1440, "height": 900},
                                        device_scale_factor=1)
            for slug, path in PAGES:
                page = ctx_d.new_page()
                try:
                    page.goto(base + path, wait_until="networkidle", timeout=30_000)
                except Exception as e:
                    print(f"[desktop] {slug} load error: {e}")
                # Give fonts + font-awesome one animation frame to render
                page.wait_for_timeout(600)
                out = f"artifacts/screenshots/desktop/{slug}.png"
                page.screenshot(path=out, full_page=True)
                print(f"  desktop {slug} -> {out}")
                page.close()
            ctx_d.close()

            # Mobile pass — iPhone 12/13 sized viewport
            ctx_m = browser.new_context(viewport={"width": 390, "height": 844},
                                        device_scale_factor=2,
                                        is_mobile=True, has_touch=True,
                                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Screenshot")
            for slug, path in PAGES:
                page = ctx_m.new_page()
                try:
                    page.goto(base + path, wait_until="networkidle", timeout=30_000)
                except Exception as e:
                    print(f"[mobile] {slug} load error: {e}")
                page.wait_for_timeout(600)
                out = f"artifacts/screenshots/mobile/{slug}.png"
                page.screenshot(path=out, full_page=True)
                print(f"  mobile  {slug} -> {out}")
                page.close()

            # Mobile nav-open screenshot on the homepage
            page = ctx_m.new_page()
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(400)
            try:
                page.click("#ra-nav-hamburger", timeout=3000)
                page.wait_for_timeout(400)
                page.screenshot(path="artifacts/screenshots/mobile/home_menu_open.png",
                                full_page=False)
                print("  mobile  home_menu_open -> artifacts/screenshots/mobile/home_menu_open.png")
            except Exception as e:
                print(f"[mobile] menu-open capture failed: {e}")
            ctx_m.close()

            # Keyboard-focus state on the home CTA
            ctx_kb = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx_kb.new_page()
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(300)
            try:
                for _ in range(6):
                    page.keyboard.press("Tab")
                page.screenshot(path="artifacts/screenshots/desktop/home_kb_focus.png",
                                full_page=False)
                print("  desktop home_kb_focus -> artifacts/screenshots/desktop/home_kb_focus.png")
            except Exception as e:
                print(f"[desktop] keyboard focus capture failed: {e}")
            ctx_kb.close()

            # Reduced motion desktop
            ctx_rm = browser.new_context(viewport={"width": 1440, "height": 900},
                                         reduced_motion="reduce")
            page = ctx_rm.new_page()
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(400)
            page.screenshot(path="artifacts/screenshots/desktop/home_reduced_motion.png",
                            full_page=False)
            print("  desktop home_reduced_motion -> artifacts/screenshots/desktop/home_reduced_motion.png")
            ctx_rm.close()

            browser.close()
    finally:
        try:
            httpd.shutdown()
        except Exception:
            pass

    print("\nscreenshots complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
