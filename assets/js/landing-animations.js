/*
 * Revelation Agency — landing-page animations + interactivity
 *
 * Hand-rolled, dependency-free. ~3 KB minified. Wires:
 *   - IntersectionObserver-driven scroll reveals (.la-reveal)
 *   - Count-up number animation (.la-counter[data-target])
 *   - Animated comparison-chart bar fills (.la-bar[data-pct])
 *   - Sticky CTA bar show/hide based on hero visibility
 *   - Before/after toggle (.la-toggle input switching .la-toggle__panel)
 *
 * Runs at DOMContentLoaded. Respects prefers-reduced-motion: skips count-ups
 * and shows revealed content immediately.
 */
(function () {
  'use strict';

  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  // ---------------- Scroll reveal -----------------------------------------
  function initReveals() {
    var els = document.querySelectorAll('.la-reveal');
    if (!els.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  // ---------------- Count-up ----------------------------------------------
  function easeOutQuart(t) { return 1 - Math.pow(1 - t, 4); }

  function animateCounter(el) {
    var target = parseFloat(el.getAttribute('data-target') || '0');
    var duration = parseInt(el.getAttribute('data-duration') || '1400', 10);
    var decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
    var start = performance.now();
    function tick(now) {
      var t = Math.min(1, (now - start) / duration);
      var v = easeOutQuart(t) * target;
      el.textContent = decimals ? v.toFixed(decimals) : Math.round(v);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function initCounters() {
    var counters = document.querySelectorAll('.la-counter[data-target]');
    if (!counters.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      counters.forEach(function (el) {
        var target = parseFloat(el.getAttribute('data-target') || '0');
        var decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
        el.textContent = decimals ? target.toFixed(decimals) : Math.round(target);
      });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { io.observe(c); });
  }

  // ---------------- Comparison bars ---------------------------------------
  function initBars() {
    var bars = document.querySelectorAll('.la-bar[data-pct]');
    if (!bars.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      bars.forEach(function (el) {
        var pct = el.getAttribute('data-pct') || '0';
        var fill = el.querySelector('.la-bar__fill');
        if (fill) fill.style.width = pct + '%';
      });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var pct = entry.target.getAttribute('data-pct') || '0';
          var fill = entry.target.querySelector('.la-bar__fill');
          if (fill) fill.style.width = pct + '%';
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    bars.forEach(function (b) { io.observe(b); });
  }

  // ---------------- Sticky CTA bar ----------------------------------------
  function initStickyCTA() {
    var bar = document.querySelector('.la-sticky-cta');
    if (!bar) return;
    var hero = document.querySelector('.la-hero');
    if (!hero) {
      bar.classList.add('is-visible');
      return;
    }
    if (!('IntersectionObserver' in window)) {
      bar.classList.add('is-visible');
      return;
    }
    var heroIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        // Show sticky bar when hero leaves the top of the viewport
        if (entry.intersectionRatio < 0.25) {
          bar.classList.add('is-visible');
        } else {
          bar.classList.remove('is-visible');
        }
      });
    }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
    heroIO.observe(hero);
  }

  // ---------------- Before/after toggle -----------------------------------
  function initToggles() {
    var toggles = document.querySelectorAll('.la-toggle');
    toggles.forEach(function (toggle) {
      var radios = toggle.querySelectorAll('input[type="radio"]');
      radios.forEach(function (r) {
        r.addEventListener('change', function () {
          var key = r.value;
          var panels = toggle.querySelectorAll('.la-toggle__panel');
          panels.forEach(function (p) {
            p.classList.toggle('is-active', p.getAttribute('data-panel') === key);
          });
          var btns = toggle.querySelectorAll('.la-toggle__btn');
          btns.forEach(function (b) {
            b.classList.toggle('is-active', b.getAttribute('data-for') === key);
          });
        });
      });
    });
  }

  ready(function () {
    initReveals();
    initCounters();
    initBars();
    initStickyCTA();
    initToggles();
  });
})();
