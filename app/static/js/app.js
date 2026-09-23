'use strict';
(() => {
  document.documentElement.classList.add('has-js');
  const toggle = document.querySelector('.tl-menu-toggle');
  const nav = document.querySelector('#site-nav');
  const mobileLanguage = document.querySelector('.tl-mobile-language');
  const setMenu = (open) => {
    if (!toggle || !nav) return;
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? toggle.dataset.closeLabel : toggle.dataset.openLabel);
    if (open && mobileLanguage) mobileLanguage.open = false;
  };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  nav?.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && mobileLanguage?.open) {
      mobileLanguage.open = false;
      mobileLanguage.querySelector('summary').focus();
    }
    if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });
  window.matchMedia('(min-width: 1051px)').addEventListener('change', (event) => {
    if (event.matches) setMenu(false);
  });
  const preview = document.querySelector('[data-preview]');
  if (!preview) return;
  const cards = [...preview.querySelectorAll('[data-profile]')];
  const savedButton = preview.querySelector('#show-saved');
  const allButton = preview.querySelector('#show-all');
  const allLink = preview.querySelector('#preview-all');
  const heading = preview.querySelector('#results-heading');
  const status = document.querySelector('#sample-status');
  let savedOnly = false;
  let statusTimeout;
  const update = () => {
    const saved = cards.filter(card => card.querySelector('.tl-save').getAttribute('aria-pressed') === 'true');
    cards.forEach(card => { card.hidden = savedOnly && !saved.includes(card); });
    preview.querySelector('#saved-count').textContent = String(saved.length);
    preview.querySelector('#saved-empty').hidden = !(savedOnly && saved.length === 0);
    allButton.hidden = !savedOnly;
    savedButton.classList.toggle('tl-app-active', savedOnly);
    savedButton.setAttribute('aria-pressed', String(savedOnly));
    allLink.classList.toggle('tl-app-active', !savedOnly);
    if (savedOnly) allLink.removeAttribute('aria-current');
    else allLink.setAttribute('aria-current', 'page');
    heading.textContent = savedOnly ? preview.dataset.savedLabel : preview.dataset.resultsLabel;
    const count = savedOnly ? saved.length : cards.length;
    preview.querySelector('.tl-result-total').textContent = (count === 1 ? preview.dataset.countOneLabel : preview.dataset.countLabel).replace('{n}', String(count));
  };
  preview.querySelectorAll('.tl-save').forEach(button => {
    button.addEventListener('click', () => {
      const saved = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(saved));
      button.setAttribute('aria-label', saved ? button.dataset.removeLabel : button.dataset.saveLabel);
      update();
      clearTimeout(statusTimeout);
      status.textContent = saved ? preview.dataset.savedMessage : preview.dataset.removedMessage;
      status.classList.add('is-visible');
      statusTimeout = setTimeout(() => status.classList.remove('is-visible'), 4200);
      if (savedOnly && !saved) savedButton.focus({ preventScroll: true });
    });
  });
  savedButton.addEventListener('click', () => { savedOnly = !savedOnly; update(); });
  allButton.addEventListener('click', () => { savedOnly = false; update(); heading.focus({ preventScroll: true }); });
  allLink.addEventListener('click', () => { savedOnly = false; update(); });
  update();
})();
