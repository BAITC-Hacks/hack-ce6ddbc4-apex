'use strict';
(() => {
  document.documentElement.classList.add('has-js');
  const toggle = document.querySelector('.tl-menu-toggle');
  const nav = document.querySelector('#site-nav');
  const setMenu = (open) => {
    if (!toggle || !nav) return;
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? toggle.dataset.closeLabel : toggle.dataset.openLabel);
  };
  toggle?.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  nav?.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      toggle.focus();
    }
  });
  window.matchMedia('(min-width: 1051px)').addEventListener('change', (event) => {
    if (event.matches) setMenu(false);
  });

  // In-page section links move keyboard focus to the section heading, not only the scroll.
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href*="#"]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey) return;
    const url = new URL(link.href, window.location.href);
    if (url.pathname !== window.location.pathname || url.search !== window.location.search || url.hash.length < 2) return;
    const target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
    const heading = target && target.matches('section') ? target.querySelector('h2') : null;
    if (!heading) return;
    if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
    window.setTimeout(() => heading.focus({ preventScroll: true }), 0);
  });
})();
