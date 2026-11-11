/* Revelation Agency — strategy call booking (replaces the GoHighLevel calendar).
   Reads open times from the Revelation n8n booking workflow and books one.
   Mount: <div id="ra-booking"></div> */
(function () {
  'use strict';
  var API = 'https://auto.revelationagency.com/webhook/';
  var root = document.getElementById('ra-booking');
  if (!root) return;

  var css = [
    '#ra-booking{background:#fff;border:1px solid rgba(23,23,23,.1);border-radius:18px;padding:28px;box-shadow:0 22px 60px rgba(0,0,0,.07);font-family:Helvetica,Arial,sans-serif;color:#171717}',
    '#ra-booking h3{margin:0 0 6px;font-size:20px}',
    '#ra-booking .rb-sub{margin:0 0 18px;color:#6c6862;font-size:15px}',
    '#ra-booking .rb-days{display:flex;gap:8px;overflow-x:auto;padding-bottom:6px;margin-bottom:16px}',
    '#ra-booking .rb-day{flex:0 0 auto;border:1px solid #d6d2cc;background:#faf9f7;border-radius:10px;padding:10px 14px;cursor:pointer;font-size:14px;text-align:center;color:#171717}',
    '#ra-booking .rb-day b{display:block;font-size:13px;text-transform:uppercase;letter-spacing:.06em}',
    '#ra-booking .rb-day[aria-pressed=true],#ra-booking .rb-slot[aria-pressed=true]{background:#c91c1d;border-color:#c91c1d;color:#fff}',
    '#ra-booking .rb-slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:8px;margin-bottom:18px}',
    '#ra-booking .rb-slot{border:1px solid #d6d2cc;background:#fff;border-radius:8px;padding:10px 6px;cursor:pointer;font-size:15px;color:#171717}',
    '#ra-booking .rb-slot:hover,#ra-booking .rb-day:hover{border-color:#c91c1d}',
    '#ra-booking label{display:block;font-size:13px;font-weight:700;margin:12px 0 4px}',
    '#ra-booking input,#ra-booking textarea{width:100%;box-sizing:border-box;border:1px solid #d6d2cc;border-radius:8px;padding:11px 12px;font:inherit;background:#faf9f7;color:#171717}',
    '#ra-booking textarea{min-height:80px}',
    '#ra-booking .rb-row{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}',
    '#ra-booking .rb-go{margin-top:18px;width:100%;border:0;border-radius:10px;padding:14px;background:#c91c1d;color:#fff;font-weight:700;font-size:16px;cursor:pointer}',
    '#ra-booking .rb-go:disabled{opacity:.6;cursor:default}',
    '#ra-booking .rb-msg{margin-top:12px;font-size:15px}',
    '#ra-booking .rb-err{color:#c91c1d}',
    '#ra-booking .rb-done{text-align:center;padding:30px 10px}',
    '#ra-booking .rb-done h3{font-size:24px}',
    '#ra-booking .rb-hp{position:absolute;left:-9999px}',
    '@media(max-width:560px){#ra-booking{padding:20px}#ra-booking .rb-row{grid-template-columns:1fr}}'
  ].join('');
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var q = new URLSearchParams(location.search), pre = { name: q.get('name') || '', phone: q.get('phone') || '', email: q.get('email') || '' };
  try { pre.name = pre.name || sessionStorage.getItem('ra_lead_name') || ''; pre.phone = pre.phone || sessionStorage.getItem('ra_lead_phone') || ''; } catch (e) {}
  var source = q.get('src') || (function () { try { return sessionStorage.getItem('ra_lead_source') || ''; } catch (e) { return ''; } })() || 'booking-page';

  var data = null, day = null, slot = null;

  root.innerHTML = '<h3>Pick a time for your free strategy call</h3><p class="rb-sub">30 minutes &middot; Blaine calls you &middot; times shown in Pacific Time</p><div class="rb-body"><p class="rb-msg">Loading open times&hellip;</p></div>';
  var body = root.querySelector('.rb-body');

  function load() {
    fetch(API + 'booking-slots', { cache: 'no-store' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { data = d; day = d.days && d.days[0] ? 0 : null; render(); })
      .catch(function () { body.innerHTML = '<p class="rb-msg rb-err">We couldn’t load the calendar. Please call <a href="tel:+15592017039">(559) 201-7039</a> or <a href="/contact.html">send us a message</a>.</p>'; });
  }

  function render() {
    if (!data || !data.days || !data.days.length) { body.innerHTML = '<p class="rb-msg">No open times in the next two weeks. Please call <a href="tel:+15592017039">(559) 201-7039</a>.</p>'; return; }
    var d = data.days[day];
    var h = '<div class="rb-days" role="group" aria-label="Choose a day">';
    data.days.forEach(function (x, i) {
      var parts = x.label.split(', ');
      h += '<button type="button" class="rb-day" data-i="' + i + '" aria-pressed="' + (i === day) + '"><b>' + esc(parts[0].slice(0, 3)) + '</b>' + esc(parts[1] || '') + '</button>';
    });
    h += '</div><div class="rb-slots" role="group" aria-label="Choose a time">';
    d.slots.forEach(function (s) { h += '<button type="button" class="rb-slot" data-s="' + esc(s.start) + '" aria-pressed="' + (slot === s.start) + '">' + esc(s.label) + '</button>'; });
    h += '</div>';
    h += '<form novalidate><div class="rb-row"><div><label for="rb-name">Name</label><input id="rb-name" name="name" autocomplete="name" value="' + esc(pre.name) + '"></div>' +
      '<div><label for="rb-phone">Phone</label><input id="rb-phone" name="phone" type="tel" autocomplete="tel" value="' + esc(pre.phone) + '"></div></div>' +
      '<div class="rb-row"><div><label for="rb-email">Email</label><input id="rb-email" name="email" type="email" autocomplete="email" value="' + esc(pre.email) + '"></div>' +
      '<div><label for="rb-biz">Business</label><input id="rb-biz" name="business" autocomplete="organization"></div></div>' +
      '<label for="rb-notes">What would you like to talk about?</label><textarea id="rb-notes" name="notes"></textarea>' +
      '<input class="rb-hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<button class="rb-go" type="submit">' + (slot ? 'Book ' + esc(labelFor(slot)) : 'Pick a time above') + '</button><div class="rb-msg" role="status"></div></form>';
    body.innerHTML = h;

    body.querySelectorAll('.rb-day').forEach(function (b) { b.onclick = function () { keep(); day = +b.dataset.i; slot = null; render(); }; });
    body.querySelectorAll('.rb-slot').forEach(function (b) { b.onclick = function () { keep(); slot = b.dataset.s; render(); var f = body.querySelector('#rb-name'); if (f && !f.value) f.focus(); }; });
    body.querySelector('form').onsubmit = submit;
  }

  function labelFor(start) {
    var d = data.days[day]; var s = (d.slots.filter(function (x) { return x.start === start; })[0] || {}).label || '';
    return d.label + ' at ' + s;
  }

  function keep() {
    var f = body.querySelector('form'); if (!f) return;
    pre.name = f.name.value; pre.phone = f.phone.value; pre.email = f.email.value;
  }

  function submit(e) {
    e.preventDefault();
    var f = e.target, msg = f.querySelector('.rb-msg'), btn = f.querySelector('.rb-go');
    msg.className = 'rb-msg';
    if (!slot) { msg.className = 'rb-msg rb-err'; msg.textContent = 'Pick a time above first.'; return; }
    var payload = { start_iso: slot, name: f.name.value.trim(), phone: f.phone.value.trim(), email: f.email.value.trim(),
      business: f.business.value.trim(), notes: f.notes.value.trim(), website: f.website.value, source: source };
    if (!payload.name || !payload.phone || !/^\S+@\S+\.\S+$/.test(payload.email)) { msg.className = 'rb-msg rb-err'; msg.textContent = 'Please add your name, phone and a valid email.'; return; }
    btn.disabled = true; msg.textContent = 'Booking your call…';
    fetch(API + 'booking-create', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok && j.ok, j: j }; }); })
      .then(function (res) {
        if (res.ok) {
          root.innerHTML = '<div class="rb-done"><h3>You’re booked.</h3><p>' + esc(res.j.label || labelFor(slot)) + '</p><p>Blaine will call you at ' + esc(payload.phone) + '. A confirmation with a calendar invite is on its way to ' + esc(payload.email) + '.</p></div>';
          try { if (window.fbq) fbq('track', 'Schedule'); } catch (x) {}
          return;
        }
        msg.className = 'rb-msg rb-err'; msg.textContent = (res.j && res.j.error) || 'That didn’t go through. Please try another time.';
        btn.disabled = false; keep(); slot = null; load();
      })
      .catch(function () { msg.className = 'rb-msg rb-err'; msg.innerHTML = 'That didn’t go through. Please call <a href="tel:+15592017039">(559) 201-7039</a>.'; btn.disabled = false; });
  }

  load();
})();
