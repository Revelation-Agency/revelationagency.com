"""Browser-level responsive release gate for the 2026 site refresh.

The verifier serves the checkout on loopback, renders representative pages at
320, 390, 768, and 1440 pixels, and checks the failures that static HTML tests
cannot see: clipped proof art, nested mobile gutters, orbit crowding, and the
three-level Portfolio accordion. It is read-only and writes no screenshots.
"""

from __future__ import annotations

import http.server
import os
import re
import socket
import threading
import time
import urllib.request
from dataclasses import dataclass


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = (320, 390, 768, 1440)
HEIGHT = 900
ROUTES = (
    ("home", "/index.html"),
    ("services", "/services.html"),
    ("branding-service", "/services/branding/index.html"),
    ("design-service", "/services/branding/design.html"),
    ("sales-systems-service", "/services/sales/index.html"),
    ("portfolio", "/portfolio.html"),
    ("portfolio-outreach", "/portfolio.html?filter=s1"),
    ("portfolio-invalid-filter", "/portfolio.html?filter=%22%5D%3Anot%28"),
    ("portfolio-branding", "/portfolio/branding.html"),
    ("portfolio-marketing", "/portfolio/marketing.html"),
    ("portfolio-sales-systems", "/portfolio/sales.html"),
    ("case-outcomes", "/portfolio/case-studies/bill-gerard-coaching.html"),
    ("case-sales-systems", "/portfolio/case-studies/net-metering-systems.html"),
    ("case-reservwise-app", "/portfolio/case-studies/reservwise-app.html"),
    ("case-revelation-portal", "/portfolio/case-studies/revelation-portal.html"),
    ("case-life-os", "/portfolio/case-studies/life-os.html"),
    ("case-trust-energy", "/portfolio/case-studies/trust-energy.html"),
    ("case-trust-energy-branding", "/portfolio/case-studies/trust-energy-branding.html"),
    ("sales-growth-engine", "/sales-growth-engine/index.html"),
    ("sales-intelligence", "/sales-intelligence/index.html"),
    ("web-hosting", "/web-hosting.html"),
)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args, **_kwargs):
        pass


class ReusableServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


@dataclass
class Failure:
    width: int
    route: str
    message: str

    def __str__(self) -> str:
        return f"{self.width}px {self.route}: {self.message}"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server():
    os.chdir(ROOT)
    port = free_port()
    server = ReusableServer(("127.0.0.1", port), QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    for _ in range(50):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=0.5).close()
            return server, port
        except Exception:
            time.sleep(0.1)
    server.shutdown()
    raise RuntimeError("local verification server did not start")


def inspect_layout(page) -> dict:
    return page.evaluate(
        """() => {
          const visible = (el) => {
            const s = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
          };
          const rect = (el) => {
            const r = el.getBoundingClientRect();
            return {left:r.left, right:r.right, top:r.top, bottom:r.bottom, width:r.width, height:r.height};
          };
          const critical = [
            '.ra-orbit', '.ra-orbit__frame', '.ra-orbit__node', '.ra-orbit__summary',
            '.ra-service-proof', '.ra-service-proof img', '.pf-card',
            '.cs-outcomes__inner', '.pf-numbers__inner'
          ];
          const boxes = [];
          for (const selector of critical) {
            document.querySelectorAll(selector).forEach((el, index) => {
              if (visible(el)) boxes.push({selector, index, ...rect(el)});
            });
          }
          const proofRatios = [...document.querySelectorAll('.ra-service-proof img')]
            .filter(visible).map((el, index) => ({index, ratio:el.getBoundingClientRect().width / el.getBoundingClientRect().height}));
          const outcomes = [...document.querySelectorAll('.cs-outcomes__inner')]
            .filter(visible).map((el, index) => {
              const content = el.querySelector('h2, .cs-outcomes__grid') || el;
              return {index, ...rect(content)};
            });
          const nodes = [...document.querySelectorAll('.ra-orbit__node')]
            .filter(visible).map((el, index) => ({
              index, ...rect(el), clientWidth:el.clientWidth, scrollWidth:el.scrollWidth,
              clientHeight:el.clientHeight, scrollHeight:el.scrollHeight
            }));
          const proofNotes = [...document.querySelectorAll('.cs-gallery__item--proof-note')]
            .filter(visible).map((el, index) => ({
              index, ...rect(el), clientWidth:el.clientWidth, scrollWidth:el.scrollWidth,
              clientHeight:el.clientHeight, scrollHeight:el.scrollHeight
            }));
          const summary = document.querySelector('.ra-orbit__summary');
          const frame = document.querySelector('.ra-orbit__frame');
          const marketing = document.querySelector('.ra-orbit__node--marketing');
          const sales = document.querySelector('.ra-orbit__node--sales');
          const orbitAnimations = frame ? [...frame.querySelectorAll('*')].filter((el) => {
            if (!visible(el)) return false;
            const s = getComputedStyle(el);
            return s.animationName !== 'none' && s.animationIterationCount === 'infinite';
          }).map((el) => ({className:el.getAttribute('class') || el.tagName, name:getComputedStyle(el).animationName})) : [];
          const canvas = document.querySelector('#hero-network');
          return {
            innerWidth: window.innerWidth,
            documentWidth: document.documentElement.scrollWidth,
            bodyWidth: document.body.scrollWidth,
            boxes, proofRatios, outcomes, nodes, proofNotes, orbitAnimations,
            frame: frame && visible(frame) ? rect(frame) : null,
            summary: summary && visible(summary) ? {...rect(summary), clientWidth:summary.clientWidth, scrollWidth:summary.scrollWidth} : null,
            lowerGap: marketing && sales && visible(marketing) && visible(sales)
              ? sales.getBoundingClientRect().left - marketing.getBoundingClientRect().right : null,
            canvasDisplay: canvas ? getComputedStyle(canvas).display : null,
            bodyText: document.body.innerText,
            heroTagline: document.querySelector('.ra-hero__tagline')?.textContent.trim() || '',
            heroIntro: document.querySelector('.ra-hero__desc')?.textContent.replace(/\\s+/g, ' ').trim() || ''
          };
        }"""
    )


def check_mobile_portfolio_menu(page, width: int, failures: list[Failure]) -> None:
    route = "home-menu"
    try:
        page.locator("#ra-nav-hamburger").click(timeout=4_000)
        portfolio = page.locator('li.has-drop:has(> a[href="/portfolio"])').first
        portfolio.locator(":scope > button.ra-nav__services-toggle").click(timeout=4_000)
        expected = (5, 4, 4)
        groups = portfolio.locator(":scope > ul.ra-drop--l2 > li.has-drop-l3")
        if groups.count() != 3:
            failures.append(Failure(width, route, f"expected 3 portfolio groups, found {groups.count()}"))
            return
        for index, leaf_count in enumerate(expected):
            group = groups.nth(index)
            toggle = group.locator(":scope > button.ra-nav__l2-toggle")
            toggle.scroll_into_view_if_needed()
            toggle.click(timeout=4_000)
            if toggle.get_attribute("aria-expanded") != "true":
                failures.append(Failure(width, route, f"portfolio group {index + 1} did not expand"))
            links = group.locator(":scope > ul.ra-drop--l3 > li > a")
            if links.count() != leaf_count:
                failures.append(Failure(width, route, f"portfolio group {index + 1} has {links.count()} links, expected {leaf_count}"))
            menu_rect = group.locator(":scope > ul.ra-drop--l3").evaluate(
                "el => { const r=el.getBoundingClientRect(); return {left:r.left,right:r.right,width:r.width,transform:getComputedStyle(el).transform}; }"
            )
            if menu_rect["left"] < -1 or menu_rect["right"] > width + 1:
                failures.append(Failure(width, route, f"portfolio group {index + 1} drifts outside viewport: {menu_rect}"))
            if menu_rect["transform"] != "none":
                failures.append(Failure(width, route, f"portfolio group {index + 1} retains transform {menu_rect['transform']}"))
        nav_rect = page.locator("#ra-nav .ra-nav__links").evaluate(
            "el => { const r=el.getBoundingClientRect(); return {left:r.left,right:r.right,width:r.width,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth}; }"
        )
        if nav_rect["left"] < -1 or nav_rect["right"] > width + 1 or nav_rect["scrollWidth"] > nav_rect["clientWidth"] + 1:
            failures.append(Failure(width, route, f"open nav drifts or overflows: {nav_rect}"))
    except Exception as exc:
        failures.append(Failure(width, route, f"accordion interaction failed: {exc}"))


def check_desktop_portfolio_menu(page, failures: list[Failure]) -> None:
    try:
        portfolio = page.locator('li.has-drop:has(> a[href="/portfolio"])').first
        portfolio.hover()
        group = portfolio.locator(":scope > ul.ra-drop--l2 > li.has-drop-l3").first
        group.hover()
        rect = group.locator(":scope > ul.ra-drop--l3").evaluate(
            "el => { const r=el.getBoundingClientRect(); return {left:r.left,right:r.right,width:r.width,display:getComputedStyle(el).display,visibility:getComputedStyle(el).visibility}; }"
        )
        if rect["left"] < -1 or rect["right"] > 1441 or rect["display"] == "none" or rect["visibility"] == "hidden":
            failures.append(Failure(1440, "home-menu", f"desktop Portfolio flyout is clipped or hidden: {rect}"))
        colors = group.locator(":scope > ul.ra-drop--l3 a").evaluate_all(
            "links => links.map(link => getComputedStyle(link).color)"
        )
        for color in colors:
            channels = [int(value) for value in re.findall(r"\d+", color)[:3]]
            if len(channels) == 3:
                def linear(channel: int) -> float:
                    value = channel / 255
                    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                foreground = 0.2126 * linear(channels[0]) + 0.7152 * linear(channels[1]) + 0.0722 * linear(channels[2])
                background = linear(16)
                contrast = (max(foreground, background) + 0.05) / (min(foreground, background) + 0.05)
                if contrast < 4.5:
                    failures.append(Failure(1440, "home-menu", f"desktop Portfolio leaf contrast is only {contrast:.2f}:1 ({color})"))
    except Exception as exc:
        failures.append(Failure(1440, "home-menu", f"desktop flyout interaction failed: {exc}"))


def main() -> int:
    from playwright.sync_api import sync_playwright

    failures: list[Failure] = []
    server, port = start_server()
    base = f"http://127.0.0.1:{port}"
    rendered = 0
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": HEIGHT},
                    is_mobile=width <= 768,
                    has_touch=width <= 768,
                    reduced_motion="no-preference",
                )
                for slug, path in ROUTES:
                    page = context.new_page()
                    local_4xx: list[str] = []
                    page_errors: list[str] = []
                    page.on(
                        "response",
                        lambda response, local_4xx=local_4xx: local_4xx.append(f"{response.status} {response.url}")
                        if response.url.startswith(base) and response.status >= 400 else None,
                    )
                    page.on("pageerror", lambda error, page_errors=page_errors: page_errors.append(str(error)))
                    try:
                        page.goto(base + path, wait_until="domcontentloaded", timeout=20_000)
                        page.wait_for_timeout(450)
                        rendered += 1
                        data = inspect_layout(page)
                        if local_4xx:
                            failures.append(Failure(width, slug, f"local HTTP failures: {local_4xx}"))
                        if page_errors:
                            failures.append(Failure(width, slug, f"page errors: {page_errors}"))
                        if data["documentWidth"] > width + 1 or data["bodyWidth"] > width + 1:
                            failures.append(Failure(width, slug, f"document overflow: html={data['documentWidth']} body={data['bodyWidth']}"))
                        for box in data["boxes"]:
                            if box["left"] < -1 or box["right"] > width + 1:
                                failures.append(Failure(width, slug, f"{box['selector']}[{box['index']}] clips horizontally: {box}"))
                        for image in data["proofRatios"]:
                            if abs(image["ratio"] - (16 / 9)) > 0.02:
                                failures.append(Failure(width, slug, f"proof image {image['index']} ratio is {image['ratio']:.3f}, expected 1.778"))
                        for note in data["proofNotes"]:
                            if note["scrollWidth"] > note["clientWidth"] + 1:
                                failures.append(Failure(width, slug, f"text gallery proof note has masked horizontal drift: {note}"))
                        if slug == "case-life-os":
                            technical_card = page.locator(".cs-service-card", has_text="Task/Idea/Reminder/Note/Resource").first
                            card_metrics = technical_card.evaluate(
                                "el => { const p=el.querySelector('p'); return {cardClient:el.clientWidth,cardScroll:el.scrollWidth,pClient:p.clientWidth,pScroll:p.scrollWidth}; }"
                            )
                            if card_metrics["cardScroll"] > card_metrics["cardClient"] + 1 or card_metrics["pScroll"] > card_metrics["pClient"] + 1:
                                failures.append(Failure(width, slug, f"technical entity list does not wrap: {card_metrics}"))
                        if slug in ("case-trust-energy", "case-trust-energy-branding"):
                            logo = page.locator("img.ra-proof-logo--trust").first
                            logo.scroll_into_view_if_needed()
                            page.wait_for_function(
                                "el => el.complete && el.naturalWidth > 0",
                                arg=logo.element_handle(),
                                timeout=4_000,
                            )
                            logo_metrics = logo.evaluate(
                                """el => {
                                  const r=el.getBoundingClientRect(), p=el.parentElement.getBoundingClientRect(), s=getComputedStyle(el);
                                  return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,parentLeft:p.left,parentRight:p.right,
                                    client:el.clientWidth,scroll:el.scrollWidth,naturalWidth:el.naturalWidth,
                                    paddingTop:parseFloat(s.paddingTop),paddingBottom:parseFloat(s.paddingBottom)};
                                }"""
                            )
                            visible_height = (logo_metrics["bottom"] - logo_metrics["top"] -
                                              logo_metrics["paddingTop"] - logo_metrics["paddingBottom"])
                            if (logo_metrics["scroll"] > logo_metrics["client"] + 1 or
                                    logo_metrics["left"] < logo_metrics["parentLeft"] - 1 or
                                    logo_metrics["right"] > logo_metrics["parentRight"] + 1 or
                                    logo_metrics["naturalWidth"] <= 0 or visible_height < 70):
                                failures.append(Failure(width, slug, f"Trust Energy logo proof is cropped or visually consumed by padding: {logo_metrics}, visibleHeight={visible_height:.1f}"))
                        if slug == "web-hosting":
                            crumb_metrics = page.locator(".wh-hero__crumbs").evaluate(
                                "el => ({client:el.clientWidth,scroll:el.scrollWidth,right:el.getBoundingClientRect().right})"
                            )
                            if crumb_metrics["scroll"] > crumb_metrics["client"] + 1 or crumb_metrics["right"] > width + 1:
                                failures.append(Failure(width, slug, f"breadcrumb clips: {crumb_metrics}"))
                        if slug in ("sales-growth-engine", "sales-intelligence") and width <= 768:
                            if slug == "sales-intelligence":
                                cover_metrics = page.locator(".slide.is-active .cover-headline").evaluate(
                                    "el => ({client:el.clientWidth,scroll:el.scrollWidth,right:el.getBoundingClientRect().right})"
                                )
                                if cover_metrics["scroll"] > cover_metrics["client"] + 1 or cover_metrics["right"] > width + 1:
                                    failures.append(Failure(width, slug, f"cover headline clips: {cover_metrics}"))
                            page.locator("#ribbonNext").click()
                            page.wait_for_timeout(850)
                            header_metrics = page.locator(".slide.is-active .slide-header").evaluate(
                                "el => ({client:el.clientWidth,scroll:el.scrollWidth,right:el.getBoundingClientRect().right,text:el.innerText})"
                            )
                            if header_metrics["scroll"] > header_metrics["client"] + 1 or header_metrics["right"] > width + 1:
                                failures.append(Failure(width, slug, f"slide header clips: {header_metrics}"))
                        if width <= 768:
                            minimum_gutter = 19 if width <= 480 else 23
                            for outcome in data["outcomes"]:
                                if outcome["left"] < minimum_gutter or width - outcome["right"] < minimum_gutter:
                                    failures.append(Failure(width, slug, f"outcomes gutter is too small: {outcome}"))
                        if slug == "home":
                            tagline = "We help with Branding, Marketing & Sales Systems"
                            intro = "Revelation Agency helps you run your Branding, Marketing, and Sales as one connected growth system — operator-led, deliberately scoped, and backed by receipts."
                            if tagline != data["heroTagline"]:
                                failures.append(Failure(width, slug, "approved hero tagline is not rendered"))
                            if intro != data["heroIntro"]:
                                failures.append(Failure(width, slug, "approved hero paragraph is not rendered"))
                            for node in data["nodes"]:
                                if node["scrollWidth"] > node["clientWidth"] + 1 or node["scrollHeight"] > node["clientHeight"] + 1:
                                    failures.append(Failure(width, slug, f"orbit node {node['index']} content overflows: {node}"))
                            if width <= 768 and data["lowerGap"] is not None and data["lowerGap"] < 11:
                                failures.append(Failure(width, slug, f"orbit lower-card gap is only {data['lowerGap']:.1f}px"))
                            if width <= 768 and data["canvasDisplay"] != "none":
                                failures.append(Failure(width, slug, f"hero canvas remains visible on mobile ({data['canvasDisplay']})"))
                            if len(data["orbitAnimations"]) > 5:
                                failures.append(Failure(width, slug, f"orbit still has {len(data['orbitAnimations'])} continuous animations: {data['orbitAnimations']}"))
                            if width in (320, 390, 768):
                                check_mobile_portfolio_menu(page, width, failures)
                            elif width == 1440:
                                check_desktop_portfolio_menu(page, failures)
                        if slug == "portfolio-outreach":
                            empty_state = page.locator("#pf-empty-state")
                            empty_text = " ".join((empty_state.text_content() or "").split())
                            if empty_state.is_hidden() or "Outreach work is not published yet." not in empty_text:
                                failures.append(Failure(width, slug, "zero-result Outreach filter does not show its explicit proof-state message"))
                        if slug == "portfolio-invalid-filter":
                            visible_cards = page.locator(".pf-card:not(.pf-card--hidden)").count()
                            if visible_cards != 21 or not page.locator("#pf-empty-state").is_hidden():
                                failures.append(Failure(width, slug, f"invalid filter did not fall back to all work ({visible_cards} visible cards)"))
                    except Exception as exc:
                        failures.append(Failure(width, slug, f"render failed: {exc}"))
                    finally:
                        page.close()
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    if failures:
        print(f"Responsive render verification FAILED ({len(failures)} issues across {rendered} renders)")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Responsive render verification PASSED ({rendered} renders: {len(ROUTES)} routes x {len(WIDTHS)} widths)")
    print("- exact homepage copy rendered at 320 / 390 / 768 / 1440")
    print("- mobile orbit contained, simplified, and spaced")
    print("- service proof art rendered at 16:9")
    print("- portfolio and outcomes gutters contained")
    print("- Portfolio 5 / 4 / 4 accordion and desktop flyout verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
