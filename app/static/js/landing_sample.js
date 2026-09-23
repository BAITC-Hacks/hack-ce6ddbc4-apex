'use strict';
(() => {
  const menuButton = document.querySelector('.tl-menu-toggle');
  const menu = document.querySelector('#mobile-menu');
  const status = document.querySelector('#sample-status');
  const cards = [...document.querySelectorAll('[data-profile]')];
  const savedButton = document.querySelector('#show-saved');
  const allButton = document.querySelector('#show-all');
  const empty = document.querySelector('#saved-empty');
  let savedOnly = false;
  let statusTimeout;
  const notify = (message) => {
    clearTimeout(statusTimeout);
    status.textContent = message;
    status.classList.add('is-visible');
    statusTimeout = setTimeout(() => status.classList.remove('is-visible'), 4200);
  };
  const closeMenu = () => {
    menu.hidden = true;
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Открыть меню');
  };
  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menu.hidden = expanded;
    menuButton.setAttribute('aria-expanded', String(!expanded));
    menuButton.setAttribute('aria-label', expanded ? 'Открыть меню' : 'Закрыть меню');
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) {
      closeMenu();
      menuButton.focus();
    }
  });
  const desktopMedia = window.matchMedia('(min-width: 721px)');
  desktopMedia.addEventListener('change', event => { if (event.matches) closeMenu(); });
  const updateSaved = () => {
    const saved = cards.filter(card => card.querySelector('[data-save]').getAttribute('aria-pressed') === 'true');
    document.querySelector('#saved-count').textContent = String(saved.length);
    cards.forEach(card => { card.hidden = savedOnly && !saved.includes(card); });
    empty.hidden = !(savedOnly && saved.length === 0);
    allButton.hidden = !savedOnly;
    savedButton.classList.toggle('tl-app-active', savedOnly);
    const searchLink = document.querySelector('.tl-app-sidebar a[href="#workspace"]');
    searchLink.classList.toggle('tl-app-active', !savedOnly);
    if (savedOnly) searchLink.removeAttribute('aria-current');
    else searchLink.setAttribute('aria-current', 'page');
    savedButton.setAttribute('aria-pressed', String(savedOnly));
    document.querySelector('#results-heading').textContent = savedOnly ? 'Сохранённые профили' : 'Три профиля для сравнения';
    document.querySelector('.tl-result-total').textContent = savedOnly ? `${saved.length} сохранено` : `${cards.length} профиля`;
  };
  document.querySelectorAll('[data-save]').forEach(button => {
    button.addEventListener('click', () => {
      const isSaved = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(isSaved));
      button.setAttribute('aria-label', `${isSaved ? 'Убрать из избранного' : 'Сохранить'} ${button.dataset.save}`);
      updateSaved();
      notify(`Профиль «${button.dataset.save}» ${isSaved ? 'сохранён на странице' : 'убран из избранного'}`);
      if (savedOnly && !isSaved) savedButton.focus({ preventScroll: true });
    });
  });
  savedButton.addEventListener('click', () => {
    savedOnly = !savedOnly;
    updateSaved();
    notify(savedOnly ? 'Показано избранное этой страницы' : 'Показаны все три профиля');
  });
  allButton.addEventListener('click', () => {
    savedOnly = false;
    updateSaved();
    document.querySelector('#results-heading').setAttribute('tabindex', '-1');
    document.querySelector('#results-heading').focus({ preventScroll: true });
  });
  document.querySelector('.tl-app-sidebar a[href="#workspace"]').addEventListener('click', () => {
    savedOnly = false;
    updateSaved();
  });
  document.querySelector('#event-brief').addEventListener('submit', event => {
    event.preventDefault();
    savedOnly = false;
    updateSaved();
    document.querySelector('#brief-status').textContent = 'Открыт фиксированный пример. Он не пересчитан по выбранным условиям.';
    document.querySelector('#workspace').scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    const resultsHeading = document.querySelector('#results-heading');
    resultsHeading.setAttribute('tabindex', '-1');
    resultsHeading.focus({ preventScroll: true });
    notify('Пример для Алматы, 17 октября, ведущего и бюджета до 1 000 000 ₸');
  });
  const focusBrief = () => {
    document.querySelector('#brief').scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    document.querySelector('#brief-city').focus({ preventScroll: true });
  };
  document.querySelector('#edit-brief').addEventListener('click', focusBrief);
  document.querySelectorAll('[data-category]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelector('#brief-category').value = button.dataset.category;
      focusBrief();
      document.querySelector('#brief-category').focus({ preventScroll: true });
      document.querySelector('#brief-status').textContent = `Выбрана категория «${button.dataset.category}». Форма показывает фиксированный пример, без пересчёта.`;
    });
  });
  updateSaved();
})();
