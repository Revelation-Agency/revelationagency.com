/* Revelation Agency — site chat widget (replaces the GoHighLevel chat widget).
   A visitor leaves a message; it goes to the Revelation lead workflow, which saves it
   and alerts Blaine. Plain JavaScript, no outside libraries. */
(function () {
  'use strict';
  if (window.__raChat) return;
  window.__raChat = true;

  var HOOK = 'https://auto.revelationagency.com/webhook/revelation-lead';
  var RED = '#c91c1d', INK = '#171717';

  var css = [
    '.rac-btn{position:fixed;right:18px;bottom:18px;z-index:2147483000;width:58px;height:58px;border-radius:50%;border:0;background:' + RED + ';color:#fff;cursor:pointer;box-shadow:0 10px 28px rgba(0,0,0,.28);display:flex;align-items:center;justify-content:center}',
    '.rac-btn:focus-visible{outline:3px solid ' + INK + ';outline-offset:3px}',
    '.rac-bubble{position:fixed;right:18px;bottom:88px;z-index:2147483000;max-width:260px;background:#fff;color:' + INK + ';border-radius:12px;padding:12px 34px 12px 14px;font:14px/1.45 Helvetica,Arial,sans-serif;box-shadow:0 10px 28px rgba(0,0,0,.18)}',
    '.rac-bubble button{position:absolute;top:6px;right:8px;border:0;background:none;font-size:18px;cursor:pointer;color:#777}',
    '.rac-panel{position:fixed;right:18px;bottom:88px;z-index:2147483001;width:340px;max-width:calc(100vw - 24px);background:#fff;color:' + INK + ';border-radius:14px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.3);font:15px/1.5 Helvetica,Arial,sans-serif;display:none}',
    '.rac-panel.open{display:block}',
    '.rac-head{background:' + INK + ';color:#fff;padding:16px 18px}',
    '.rac-head strong{display:block;font-size:16px}',
    '.rac-head span{font-size:13px;opacity:.75}',
    '.rac-body{padding:14px 18px 18px}',
    '.rac-body label{display:block;font-size:13px;font-weight:700;margin:10px 0 4px}',
    '.rac-body input,.rac-body textarea{width:100%;box-sizing:border-box;border:1px solid #d6d2cc;border-radius:8px;padding:10px 12px;font:inherit;color:inherit;background:#faf9f7}',
    '.rac-body textarea{min-height:84px;resize:vertical}',
    '.rac-send{margin-top:14px;width:100%;border:0;border-radius:8px;padding:12px;background:' + RED + ';color:#fff;font-weight:700;font-size:15px;cursor:pointer}',
    '.rac-send:disabled{opacity:.6;cursor:default}',
    '.rac-msg{margin-top:10px;font-size:14px}',
    '.rac-msg.err{color:' + RED + '}',
    '.rac-hp{position:absolute;left:-9999px}',
    '@media(max-width:480px){.rac-panel{right:12px;left:12px;width:auto;bottom:84px}}'
  ].join('');

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (html) n.innerHTML = html;
    return n;
  }

  function init() {
    var style = el('style'); style.textContent = css; document.head.appendChild(style);

    var btn = el('button', { 'class': 'rac-btn', type: 'button', 'aria-label': 'Chat with Revelation Agency', 'aria-expanded': 'false' },
      '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>');

    var panel = el('div', { 'class': 'rac-panel', role: 'dialog', 'aria-label': 'Send us a message' },
      '<div class="rac-head"><strong>Revelation Agency</strong><span>Leave a message and Blaine will get back to you, usually the same day.</span></div>' +
      '<form class="rac-body" novalidate>' +
      '<label for="rac-name">Name</label><input id="rac-name" name="name" autocomplete="name">' +
      '<label for="rac-contact">Phone or email</label><input id="rac-contact" name="contact" autocomplete="email">' +
      '<label for="rac-text">How can we help?</label><textarea id="rac-text" name="message"></textarea>' +
      '<input class="rac-hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<button class="rac-send" type="submit">Send message</button>' +
      '<div class="rac-msg" role="status"></div></form>');

    document.body.appendChild(panel);
    document.body.appendChild(btn);

    var seen = false;
    try { seen = sessionStorage.getItem('rac_seen') === '1'; } catch (e) {}
    if (!seen) {
      setTimeout(function () {
        if (panel.classList.contains('open')) return;
        var bub = el('div', { 'class': 'rac-bubble' }, 'Questions about growing your business? Send us a message.<button type="button" aria-label="Close">&times;</button>');
        bub.querySelector('button').onclick = function () { bub.remove(); };
        bub.onclick = function (e) { if (e.target.tagName !== 'BUTTON') { bub.remove(); toggle(true); } };
        document.body.appendChild(bub);
        try { sessionStorage.setItem('rac_seen', '1'); } catch (e) {}
      }, 8000);
    }

    function toggle(open) {
      var b = document.querySelector('.rac-bubble'); if (b) b.remove();
      var isOpen = typeof open === 'boolean' ? open : !panel.classList.contains('open');
      panel.classList.toggle('open', isOpen);
      btn.setAttribute('aria-expanded', String(isOpen));
      if (isOpen) panel.querySelector('#rac-name').focus();
    }
    btn.onclick = function () { toggle(); };
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && panel.classList.contains('open')) toggle(false); });

    var form = panel.querySelector('form'), send = panel.querySelector('.rac-send'), msg = panel.querySelector('.rac-msg');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.website.value) return;
      var name = form.name.value.trim(), contact = form.contact.value.trim(), text = form.message.value.trim();
      msg.className = 'rac-msg';
      if (!contact || !text) { msg.className = 'rac-msg err'; msg.textContent = 'Add a phone or email and a short message.'; return; }
      var isEmail = /@/.test(contact);
      var payload = {
        name: name, email: isEmail ? contact : '', phone: isEmail ? '' : contact, message: text,
        source: 'chat-widget', page: location.pathname + location.search, referrer: document.referrer || ''
      };
      send.disabled = true; msg.textContent = 'Sending...';
      fetch(HOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); form.reset(); msg.textContent = 'Got it — thank you! We’ll be in touch soon.'; })
        .catch(function () { msg.className = 'rac-msg err'; msg.innerHTML = 'That didn’t go through. Please call <a href="tel:+15592017039">(559) 201-7039</a>.'; })
        .finally(function () { send.disabled = false; });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
