/* Designbook interactions are local specimens. No requests, accounts, or persistence. */
(() => {
  'use strict';
  const toast = document.getElementById('db-toast');
  let toastTimer;
  function announce(message) { clearTimeout(toastTimer); toast.textContent = message; toastTimer = setTimeout(() => { toast.textContent = ''; }, 5500); }
  document.querySelectorAll('[data-demo]').forEach(button => button.addEventListener('click', () => announce(button.dataset.demo)));
  document.querySelectorAll('[aria-disabled="true"]').forEach(button => button.addEventListener('click', e => e.preventDefault()));
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(button.dataset.copy); announce(`Скопировано: ${button.dataset.copy}`); }
    catch { announce(`Код цвета: ${button.dataset.copy}. Выделите и скопируйте его вручную.`); }
  }));
  document.querySelectorAll('[data-favourite]').forEach(button => {
    const initialName = button.getAttribute('aria-label');
    button.addEventListener('click', () => { const selected = button.getAttribute('aria-pressed') !== 'true'; button.setAttribute('aria-pressed', String(selected)); button.textContent = selected ? '♥' : '♡'; button.setAttribute('aria-label', selected ? initialName.replace('Добавить', 'Убрать').replace('в избранное', 'из избранного') : initialName); announce(selected ? 'Образец сохранён до перезагрузки страницы.' : 'Образец убран из избранного.'); });
  });
  const loader = document.getElementById('db-loading-demo');
  loader.addEventListener('click', () => { if (loader.disabled) return; loader.disabled = true; loader.setAttribute('aria-busy', 'true'); loader.textContent = 'Подбираем…'; setTimeout(() => { loader.disabled = false; loader.removeAttribute('aria-busy'); loader.textContent = 'Проверить загрузку →'; announce('Загрузка завершена. Это демонстрация состояния кнопки.'); }, 1100); });
  const dialog = document.getElementById('db-delete-dialog');
  const openDialog = document.getElementById('db-open-dialog');
  openDialog.addEventListener('click', () => dialog.showModal());
  dialog.addEventListener('close', () => { openDialog.focus(); if (dialog.returnValue === 'delete') announce('Подтверждение выполнено. Реальные данные не менялись.'); dialog.returnValue = ''; });
  document.querySelectorAll('[data-password]').forEach(button => button.addEventListener('click', () => { const field = document.getElementById(button.dataset.password); const visible = field.type === 'password'; field.type = visible ? 'text' : 'password'; button.textContent = visible ? 'Скрыть' : 'Показать'; button.setAttribute('aria-pressed', String(visible)); }));
  document.querySelectorAll('[data-demo-form]').forEach(form => form.addEventListener('submit', event => { event.preventDefault(); const status = form.querySelector('[data-form-status]'); status.textContent = form.dataset.demoForm === 'search' ? 'Форма проверена. Для демонстрации сохранён фиксированный пример; реальный движок здесь не вызывается.' : 'Форма заполнена корректно. Это образец: данные не отправлены, аккаунт и сессия не созданы.'; }));
  const phrases = {ru:'Выбор с объяснением.', kk:'Таңдау себебі түсінікті.', en:'A choice you can explain.'};
  document.querySelectorAll('[data-sample-lang]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('[data-sample-lang]').forEach(item => item.setAttribute('aria-pressed', String(item === button))); const sample = document.getElementById('db-language-sample'); sample.lang = button.dataset.sampleLang; sample.textContent = phrases[button.dataset.sampleLang]; }));
  const tabs = [...document.querySelectorAll('[data-phase]')];
  function selectPhase(number, focus = false) { tabs.forEach(tab => { const active = tab.dataset.phase === String(number); tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1; document.getElementById(tab.getAttribute('aria-controls')).hidden = !active; if (active && focus) tab.focus(); }); }
  tabs.forEach((tab, index) => { tab.addEventListener('click', () => selectPhase(tab.dataset.phase)); tab.addEventListener('keydown', event => { let next; if (event.key === 'ArrowRight') next = (index + 1) % tabs.length; if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length; if (event.key === 'Home') next = 0; if (event.key === 'End') next = tabs.length - 1; if (next !== undefined) { event.preventDefault(); selectPhase(tabs[next].dataset.phase, true); } }); });
  document.querySelectorAll('[data-go-phase]').forEach(button => button.addEventListener('click', event => { event.preventDefault(); selectPhase(button.dataset.goPhase, true); document.getElementById('screens').scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block:'start'}); }));
  document.querySelectorAll('[data-calendar-day]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('[data-calendar-day]').forEach(item => item.setAttribute('aria-pressed', String(item === button))); announce(`${button.dataset.calendarDay} октября выбрано в образце календаря.`); }));
  const navLinks = [...document.querySelectorAll('.db-sidebar nav a')];
  if ('IntersectionObserver' in window) { const observer = new IntersectionObserver(entries => { entries.forEach(entry => { if (entry.isIntersecting) navLinks.forEach(link => { if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); }); }); }, {rootMargin:'-18% 0px -65% 0px'}); navLinks.forEach(link => { const section = document.querySelector(link.hash); if (section) observer.observe(section); }); }
})();
