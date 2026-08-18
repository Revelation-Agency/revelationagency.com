/**
 * Revelation Agency — 2026 experience layer
 * Progressive enhancement only: content remains visible if JavaScript fails.
 */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function each(nodes, callback) {
    Array.prototype.forEach.call(nodes, callback);
  }

  function revealInView(targets) {
    each(targets, function (element) {
      var rect = element.getBoundingClientRect();
      if (rect.top <= window.innerHeight * 1.08 && rect.bottom >= -40) {
        element.classList.add("visible");
      }
    });
  }

  function setupRevealMotion() {
    var targets = doc.querySelectorAll(".fade-up, .fade-in, .reveal-on-scroll");

    // Mark everything already in view before enabling hidden pre-reveal styles.
    revealInView(targets);
    root.classList.add("ra-motion-ready");

    if (reduceMotion) {
      each(targets, function (element) {
        element.classList.add("visible");
      });
      return;
    }

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          each(entries, function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("visible");
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.01, rootMargin: "0px 0px 12% 0px" }
      );

      each(targets, function (element) {
        if (!element.classList.contains("visible")) observer.observe(element);
      });
    } else {
      each(targets, function (element) {
        element.classList.add("visible");
      });
    }

    // A small independent safety net protects content if another page-local
    // observer is misconfigured or disconnected during navigation restore.
    window.addEventListener(
      "scroll",
      function () {
        revealInView(targets);
      },
      { passive: true }
    );
    window.addEventListener("pageshow", function () {
      revealInView(targets);
    });
  }

  function setupScrollState() {
    var progress = doc.createElement("div");
    progress.className = "ra-scroll-progress";
    progress.setAttribute("aria-hidden", "true");
    doc.body.appendChild(progress);

    var nav = doc.querySelector(".ra-nav, nav");
    var ticking = false;

    function update() {
      var max = Math.max(1, doc.documentElement.scrollHeight - window.innerHeight);
      var ratio = Math.max(0, Math.min(1, window.scrollY / max));
      root.style.setProperty("--ra-scroll", ratio.toFixed(4));
      if (nav) nav.classList.toggle("ra-nav--scrolled", window.scrollY > 18);
      ticking = false;
    }

    function requestUpdate() {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    }

    update();
    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate, { passive: true });
  }

  function setupTilt() {
    if (
      reduceMotion ||
      !window.matchMedia ||
      !window.matchMedia("(hover: hover) and (pointer: fine)").matches
    ) {
      return;
    }

    var cards = doc.querySelectorAll(".pf-card, .p-leaf, .cs-service-card, .cs-cross__card");
    each(cards, function (card) {
      card.setAttribute("data-ra-tilt", "true");
      card.addEventListener("pointermove", function (event) {
        var rect = card.getBoundingClientRect();
        var x = (event.clientX - rect.left) / rect.width - 0.5;
        var y = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--ra-tilt-x", (-y * 3).toFixed(2) + "deg");
        card.style.setProperty("--ra-tilt-y", (x * 3).toFixed(2) + "deg");
      });
      card.addEventListener("pointerleave", function () {
        card.style.setProperty("--ra-tilt-x", "0deg");
        card.style.setProperty("--ra-tilt-y", "0deg");
      });
    });
  }

  function updateFooterYear() {
    var year = String(new Date().getFullYear());
    each(doc.querySelectorAll("[data-ra-current-year]"), function (element) {
      element.textContent = year;
    });
  }

  function tuneChatWidget() {
    if (!window.matchMedia || !window.matchMedia("(max-width: 767px)").matches) return;

    var attempts = 0;
    var timer = window.setInterval(function () {
      attempts += 1;
      var host = doc.querySelector("chat-widget");
      var shadow = host && host.shadowRoot;

      if (shadow && !shadow.querySelector("style[data-ra-chat-mobile]")) {
        var style = doc.createElement("style");
        style.setAttribute("data-ra-chat-mobile", "true");
        style.textContent =
          ".lc_text-widget--prompt{display:none!important}" +
          ".lc_text-widget{height:58px!important;min-height:58px!important}";
        shadow.appendChild(style);
        window.clearInterval(timer);
      } else if (shadow || attempts >= 40) {
        window.clearInterval(timer);
      }
    }, 125);
  }

  function boot() {
    setupRevealMotion();
    setupScrollState();
    setupTilt();
    updateFooterYear();
    tuneChatWidget();
    doc.body.classList.add("ra-page-ready");
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
