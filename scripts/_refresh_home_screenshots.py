"""Tightly scoped home-only screenshot refresh for the trust-strip repair.

Only re-renders the home surfaces directly affected by the homepage hero
trust-strip label change: desktop/home.png, mobile/home.png, and
mobile/home_menu_open.png. Uses the same local 127.0.0.1 server and
viewport parameters as scripts/take_screenshots.py to keep the packet
consistent.
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

            # Desktop home
            ctx_d = browser.new_context(viewport={"width": 1440, "height": 900},
                                        device_scale_factor=1)
            page = ctx_d.new_page()
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(600)
            page.screenshot(path="artifacts/screenshots/desktop/home.png", full_page=True)
            print("  desktop home -> artifacts/screenshots/desktop/home.png")
            page.close()
            ctx_d.close()

            # Mobile home + menu open
            ctx_m = browser.new_context(viewport={"width": 390, "height": 844},
                                        device_scale_factor=2,
                                        is_mobile=True, has_touch=True,
                                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Screenshot")
            page = ctx_m.new_page()
            page.goto(base + "/index.html", wait_until="networkidle", timeout=30_000)
            page.wait_for_timeout(600)
            page.screenshot(path="artifacts/screenshots/mobile/home.png", full_page=True)
            print("  mobile  home -> artifacts/screenshots/mobile/home.png")
            page.close()

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

            browser.close()
    finally:
        try:
            httpd.shutdown()
        except Exception:
            pass

    print("\nhome-surface screenshots refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
