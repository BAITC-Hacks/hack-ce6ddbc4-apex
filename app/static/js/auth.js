// Phase 2: progressive enhancement for account forms. Without JS the forms work the same.
(function () {
  document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
    var inputs = (button.getAttribute('aria-controls') || '').split(/\s+/)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!inputs.length) return;
    button.hidden = false;
    button.addEventListener('click', function () {
      var show = button.getAttribute('aria-pressed') !== 'true';
      inputs.forEach(function (input) { input.type = show ? 'text' : 'password'; });
      button.setAttribute('aria-pressed', String(show));
    });
  });

  var idleContent = new WeakMap();

  document.querySelectorAll('form[data-busy-label]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      var submit = form.querySelector('[type="submit"]');
      if (!submit) return;
      if (submit.getAttribute('aria-busy') === 'true') {
        event.preventDefault(); // second click while the first request is in flight
        return;
      }
      form.querySelectorAll('[data-password-toggle][aria-pressed="true"]').forEach(function (button) {
        button.click(); // password managers expect type=password on submit
      });
      idleContent.set(submit, Array.prototype.slice.call(submit.childNodes));
      submit.setAttribute('aria-busy', 'true');
      submit.textContent = form.getAttribute('data-busy-label');
    });
  });

  // A page restored from the back/forward cache would keep the busy label; put the original back.
  window.addEventListener('pageshow', function (event) {
    if (!event.persisted) return;
    document.querySelectorAll('form[data-busy-label] [type="submit"][aria-busy="true"]').forEach(function (submit) {
      submit.removeAttribute('aria-busy');
      submit.replaceChildren.apply(submit, idleContent.get(submit) || []);
    });
  });
})();
