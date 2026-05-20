/**
 * Revelation Agency — Contact Form Handler
 * Client-side AJAX form submission for Vercel static hosting.
 * Configure FORM_ENDPOINT below with your preferred service
 * (Formspree, Web3Forms, Getform, etc.)
 */
(function () {
  'use strict';

  // ------- CONFIGURATION -------
  // Replace with your actual form endpoint when ready:
  // Formspree:  https://formspree.io/f/YOUR_ID
  // Web3Forms: https://api.web3forms.com/submit
  var FORM_ENDPOINT = 'https://formspree.io/f/CONFIGURE_ME';

  var form = document.getElementById('contact-form');
  var msgEl = document.querySelector('.form-message');
  var submitBtn = form ? form.querySelector('button[type="submit"]') : null;

  if (!form || !submitBtn) return;

  var btnOriginal = submitBtn.innerHTML;

  // Honeypot — bots fill hidden fields
  var hp = document.createElement('input');
  hp.type = 'text';
  hp.name = '_gotcha';
  hp.tabIndex = -1;
  hp.autocomplete = 'off';
  hp.style.cssText = 'position:absolute;left:-9999px;top:-9999px;height:0;width:0;overflow:hidden;opacity:0;pointer-events:none;';
  form.appendChild(hp);

  // Client-side validation
  function validate() {
    var email = form.querySelector('[name="email"]');
    var phone = form.querySelector('[name="phone"]');
    var name = form.querySelector('[name="name"]');
    var message = form.querySelector('[name="message"]');

    if (!name.value.trim() || !email.value.trim() || !message.value.trim()) {
      showMsg('Please fill in all required fields.', 'error');
      return false;
    }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      showMsg('Please enter a valid email address.', 'error');
      return false;
    }
    if (phone && phone.value.trim() && !/^[\d\s\-\+\(\)\.]{7,20}$/.test(phone.value.trim())) {
      showMsg('Please enter a valid phone number.', 'error');
      return false;
    }
    // Honeypot check
    if (hp.value) return false;
    return true;
  }

  function showMsg(text, type) {
    if (!msgEl) return;
    msgEl.textContent = text;
    msgEl.style.display = 'block';
    msgEl.style.padding = '14px 20px';
    msgEl.style.borderRadius = '8px';
    msgEl.style.fontSize = '15px';
    msgEl.style.fontFamily = 'Inter, system-ui, sans-serif';
    if (type === 'success') {
      msgEl.style.background = 'rgba(34,197,94,.12)';
      msgEl.style.border = '1px solid rgba(34,197,94,.3)';
      msgEl.style.color = '#22c55e';
    } else {
      msgEl.style.background = 'rgba(239,68,68,.12)';
      msgEl.style.border = '1px solid rgba(239,68,68,.3)';
      msgEl.style.color = '#ef4444';
    }
  }

  function setLoading(loading) {
    if (loading) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span><i class="fa-light fa-spinner-third fa-spin me-2"></i>Sending...</span>';
      submitBtn.style.opacity = '.6';
    } else {
      submitBtn.disabled = false;
      submitBtn.innerHTML = btnOriginal;
      submitBtn.style.opacity = '1';
    }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    if (msgEl) msgEl.style.display = 'none';

    var data = new FormData(form);

    fetch(FORM_ENDPOINT, {
      method: 'POST',
      body: data,
      headers: { 'Accept': 'application/json' }
    })
      .then(function (res) {
        setLoading(false);
        if (res.ok) {
          showMsg('Message sent successfully. We\'ll be in touch within one business day.', 'success');
          form.reset();
        } else {
          return res.json().then(function (json) {
            var msg = (json.errors && json.errors.map(function (e) { return e.message; }).join(', ')) || 'Something went wrong. Please try again.';
            showMsg(msg, 'error');
          });
        }
      })
      .catch(function () {
        setLoading(false);
        showMsg('Network error. Please check your connection and try again.', 'error');
      });
  });
})();
