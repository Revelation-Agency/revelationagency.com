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

  function setupOrbitMotion() {
    var frame = doc.querySelector(".ra-orbit__frame");
    if (!frame || reduceMotion) return;

    var orbit = frame.closest(".ra-orbit");
    if ("IntersectionObserver" in window && orbit) {
      var observer = new IntersectionObserver(
        function (entries) {
          each(entries, function (entry) {
            frame.classList.toggle("ra-orbit--active", entry.isIntersecting);
          });
        },
        { threshold: 0.12 }
      );
      observer.observe(orbit);
    } else {
      frame.classList.add("ra-orbit--active");
    }

    if (!window.matchMedia || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    frame.addEventListener("pointermove", function (event) {
      var rect = frame.getBoundingClientRect();
      var x = (event.clientX - rect.left) / rect.width - 0.5;
      var y = (event.clientY - rect.top) / rect.height - 0.5;
      frame.style.setProperty("--ra-orbit-pan-x", (x * 9).toFixed(2) + "px");
      frame.style.setProperty("--ra-orbit-pan-y", (y * 9).toFixed(2) + "px");
      frame.style.setProperty("--ra-orbit-route-x", (-x * 3.2).toFixed(2) + "px");
      frame.style.setProperty("--ra-orbit-route-y", (-y * 3.2).toFixed(2) + "px");
      frame.style.setProperty("--ra-orbit-rotate-x", (-y * 1.25).toFixed(2) + "deg");
      frame.style.setProperty("--ra-orbit-rotate-y", (x * 1.25).toFixed(2) + "deg");
    });

    frame.addEventListener("pointerleave", function () {
      frame.style.setProperty("--ra-orbit-pan-x", "0px");
      frame.style.setProperty("--ra-orbit-pan-y", "0px");
      frame.style.setProperty("--ra-orbit-route-x", "0px");
      frame.style.setProperty("--ra-orbit-route-y", "0px");
      frame.style.setProperty("--ra-orbit-rotate-x", "0deg");
      frame.style.setProperty("--ra-orbit-rotate-y", "0deg");
    });
  }

  function updateFooterYear() {
    var year = String(new Date().getFullYear());
    each(doc.querySelectorAll("[data-ra-current-year]"), function (element) {
      element.textContent = year;
    });
  }

  function setupMobileNavigation() {
    var nav = doc.getElementById("ra-nav");
    if (!nav || !window.matchMedia) return;

    var mobileQuery = window.matchMedia("(max-width: 1199px)");
    var hamburger = nav.querySelector(".ra-nav__hamburger");

    function resetBranch(branch) {
      if (!branch) return;
      branch.classList.remove("is-open");
      each(branch.querySelectorAll(".ra-drop.open"), function (drop) {
        drop.classList.remove("open");
      });
      each(branch.querySelectorAll(".ra-nav__services-toggle, .ra-nav__l2-toggle"), function (button) {
        button.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
      });
      each(branch.querySelectorAll(".has-drop-l3.is-open"), function (item) {
        item.classList.remove("is-open");
      });
    }

    function setDrawer(open) {
      nav.classList.toggle("is-open", open);
      doc.body.classList.toggle("ra-mobile-nav-open", open);
      if (hamburger) hamburger.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open) {
        each(nav.querySelectorAll(".ra-nav__links > li.has-drop"), resetBranch);
      }
    }

    function toggleTopLevel(button) {
      var branch = button.closest(".ra-nav__links > li.has-drop");
      if (!branch) return;
      var drop = branch.querySelector(":scope > .ra-drop--l2");
      if (!drop) return;
      var open = !branch.classList.contains("is-open");

      each(nav.querySelectorAll(".ra-nav__links > li.has-drop"), function (sibling) {
        if (sibling !== branch) resetBranch(sibling);
      });
      resetBranch(branch);
      branch.classList.toggle("is-open", open);
      drop.classList.toggle("open", open);
      button.classList.toggle("open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    }

    function toggleSecondLevel(button) {
      var branch = button.closest(".has-drop-l3");
      if (!branch) return;
      var drop = branch.querySelector(":scope > .ra-drop--l3");
      if (!drop) return;
      var open = !branch.classList.contains("is-open");
      var list = branch.parentElement;

      if (list) {
        each(list.querySelectorAll(":scope > .has-drop-l3"), function (sibling) {
          if (sibling !== branch) resetBranch(sibling);
        });
      }
      resetBranch(branch);
      branch.classList.toggle("is-open", open);
      drop.classList.toggle("open", open);
      button.classList.toggle("open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
    }

    nav.addEventListener(
      "click",
      function (event) {
        if (!mobileQuery.matches) return;
        var target = event.target;
        if (!target || !target.closest) return;

        var hamburgerTarget = target.closest(".ra-nav__hamburger");
        if (hamburgerTarget) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
          setDrawer(!nav.classList.contains("is-open"));
          return;
        }

        var secondToggle = target.closest(".ra-nav__l2-toggle");
        if (secondToggle) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
          toggleSecondLevel(secondToggle);
          return;
        }

        var topToggle = target.closest(".ra-nav__services-toggle");
        if (topToggle) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
          toggleTopLevel(topToggle);
          return;
        }

        var anchor = target.closest(".ra-nav__links a");
        if (!anchor) return;
        var href = anchor.getAttribute("href");
        if (!href || href.charAt(0) === "#") return;

        // On mobile, labels are links and chevrons are accordion controls.
        // Stop the retired page-local handlers from turning a page tap into
        // an off-canvas animation, then navigate deterministically.
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        setDrawer(false);
        window.location.assign(anchor.href);
      },
      true
    );

    doc.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        setDrawer(false);
        if (hamburger) hamburger.focus();
      }
    });

    function closeAtDesktop() {
      if (!mobileQuery.matches) setDrawer(false);
    }
    if (mobileQuery.addEventListener) mobileQuery.addEventListener("change", closeAtDesktop);
    else if (mobileQuery.addListener) mobileQuery.addListener(closeAtDesktop);
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
    setupOrbitMotion();
    setupMobileNavigation();
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
