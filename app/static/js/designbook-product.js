/* Local design specimens. Nothing is submitted or persisted. */
(() => {
  'use strict';
  const form = document.getElementById('td-brief-form');
  if (!form) return;
  const money = value => new Intl.NumberFormat('ru-RU').format(value) + ' ₸';
  const dateText = value => {
    if (!value || !/^2026-\d{2}-\d{2}$/.test(value)) return 'Выберите дату';
    return new Intl.DateTimeFormat('ru-RU', {day:'numeric',month:'long',year:'numeric'}).format(new Date(value + 'T12:00:00')).replace(' г.', '');
  };
  const budget = document.getElementById('td-budget');
  const range = document.getElementById('td-budget-range');
  const hours = document.getElementById('td-hours');
  const date = document.getElementById('td-date');
  const wishes = document.getElementById('td-wishes');
  const status = document.getElementById('td-brief-status');
  const field = name => new FormData(form).get(name);
  const languageLabels = {'':'Любой','русский':'Русский','казахский':'Қазақша','английский':'English'};
  function updateSummary() {
    const format = String(field('event_format'));
    const title = format.charAt(0).toUpperCase() + format.slice(1);
    document.getElementById('td-summary-title').textContent = title + ' · ' + field('city');
    document.getElementById('td-summary-category').textContent = field('category');
    document.getElementById('td-summary-date').textContent = dateText(date.value);
    document.getElementById('td-summary-budget').textContent = budget.value && Number(budget.value) > 0 ? money(Number(budget.value)) : 'Укажите сумму';
    document.getElementById('td-summary-hours').textContent = hours.value ? hours.value + ' ч' : 'Без ограничения';
    document.getElementById('td-summary-language').textContent = languageLabels[field('language')];
    document.querySelector('[data-hours-step="-1"]').disabled = !!hours.value && Number(hours.value) <= 1;
    document.querySelector('[data-hours-step="1"]').disabled = !!hours.value && Number(hours.value) >= 24;
    document.getElementById('td-wishes-count').textContent = wishes.value.length + ' / 500';
    status.textContent = '';
  }
  function syncBudget() {
    const amount = Number(budget.value);
    if (budget.value && Number.isFinite(amount) && amount > 0) {
      range.min = String(Math.min(100000, amount));
      range.max = String(Math.max(3000000, Math.ceil(amount / 100000) * 100000));
      range.step = '1';
      range.value = String(amount);
      document.getElementById('td-budget-max').textContent = money(Number(range.max));
      document.querySelector('.td-range-labels>span').textContent = money(Number(range.min));
    }
    document.querySelectorAll('[data-budget]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.budget) === amount)));
  }
  budget.addEventListener('input', syncBudget);
  range.addEventListener('input', () => { budget.value = range.value; syncBudget(); updateSummary(); });
  document.querySelectorAll('[data-budget]').forEach(button => button.addEventListener('click', () => { budget.value = button.dataset.budget; syncBudget(); updateSummary(); }));
  document.querySelectorAll('[data-hours-step]').forEach(button => button.addEventListener('click', () => {
    hours.value = String(Math.max(1, Math.min(24, (Number(hours.value) || 0) + Number(button.dataset.hoursStep))));
    updateSummary();
  }));
  document.getElementById('td-hours-clear').addEventListener('click', () => { hours.value = ''; updateSummary(); });
  form.addEventListener('input', updateSummary);
  form.addEventListener('change', updateSummary);
  form.addEventListener('submit', event => { event.preventDefault(); status.textContent = 'Поля заполнены. В этом образце подбор не выполняется.'; });
  const calendar = document.getElementById('td-date-grid');
  const disclosure = document.querySelector('.td-calendar-disclosure');
  let month = 9;
  const monthNames = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь'];
  const shortMonths = ['ЯНВ','ФЕВ','МАР','АПР','МАЙ','ИЮН','ИЮЛ','АВГ','СЕН','ОКТ','НОЯ','ДЕК'];
  const isoDate = (m, day) => `2026-${String(m + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
  function renderCalendar() {
    const name = monthNames[month];
    document.getElementById('td-calendar-month').textContent = name.charAt(0).toUpperCase() + name.slice(1) + ' 2026';
    document.querySelector('[data-month-step="-1"]').disabled = month === 8;
    document.querySelector('[data-month-step="1"]').disabled = month === 11;
    calendar.replaceChildren();
    const offset = (new Date(2026, month, 1).getDay() + 6) % 7;
    for (let i = 0; i < offset; i++) calendar.append(document.createElement('span'));
    const count = new Date(2026, month + 1, 0).getDate();
    let firstValid;
    let selected;
    for (let day = 1; day <= count; day++) {
      const button = document.createElement('button');
      const value = isoDate(month, day);
      button.type = 'button'; button.textContent = String(day); button.dataset.date = value;
      button.setAttribute('aria-label', dateText(value)); button.setAttribute('aria-pressed', String(value === date.value));
      button.disabled = value < date.min || value > date.max; button.tabIndex = -1;
      if (!button.disabled && !firstValid) firstValid = button;
      if (value === date.value) selected = button;
      calendar.append(button);
    }
    if (selected || firstValid) (selected || firstValid).tabIndex = 0;
  }
  calendar.addEventListener('click', event => {
    const button = event.target.closest('button[data-date]');
    if (!button || button.disabled) return;
    date.value = button.dataset.date; updateDate(); updateSummary();
    disclosure.open = false; disclosure.querySelector('summary').focus();
  });
  calendar.addEventListener('keydown', event => {
    const steps = {ArrowRight:1,ArrowLeft:-1,ArrowDown:7,ArrowUp:-7};
    const buttons = [...calendar.querySelectorAll('button:not(:disabled)')];
    const index = buttons.indexOf(document.activeElement);
    if (index < 0) return;
    let next;
    if (event.key in steps) next = Math.max(0,Math.min(buttons.length-1,index+steps[event.key]));
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = buttons.length-1;
    if (next !== undefined) { event.preventDefault(); buttons.forEach(item => item.tabIndex = -1); buttons[next].tabIndex = 0; buttons[next].focus(); }
  });
  disclosure.addEventListener('keydown', event => { if (event.key === 'Escape') { disclosure.open=false; disclosure.querySelector('summary').focus(); } });
  document.querySelectorAll('[data-month-step]').forEach(button => button.addEventListener('click', () => { month = Math.max(8,Math.min(11,month + Number(button.dataset.monthStep))); renderCalendar(); }));
  function updateDate() {
    if (date.value && date.validity.valid) {
      const parts = date.value.split('-').map(Number);
      month = parts[1]-1;
      document.getElementById('td-date-day').textContent = String(parts[2]);
      document.getElementById('td-date-month').textContent = shortMonths[month];
    } else { document.getElementById('td-date-day').textContent = '–'; document.getElementById('td-date-month').textContent = 'ДАТА'; }
    renderCalendar();
  }
  date.addEventListener('input', updateDate);
  date.addEventListener('change', updateDate);
  const email = document.getElementById('td-email');
  email.addEventListener('blur', () => {
    const invalid = !!email.value && !email.validity.valid;
    email.setAttribute('aria-invalid', String(invalid));
    document.getElementById('td-email-status').textContent = invalid ? 'Введите полный адрес, например name@example.com.' : email.value ? 'Формат адреса верный.' : 'Проверка формата при выходе из поля';
  });
  document.getElementById('td-password').addEventListener('input', event => {
    const value = event.target.value;
    const rules = {length:value.length >= 8,letter:/\p{L}/u.test(value),number:/[0-9]/.test(value)};
    Object.entries(rules).forEach(([name,valid]) => document.querySelector(`[data-rule="${name}"]`).dataset.valid = String(valid));
  });
  document.querySelectorAll('[data-save-card]').forEach(button => {
    const name = button.getAttribute('aria-label');
    button.addEventListener('click', () => { const selected = button.getAttribute('aria-pressed') !== 'true'; button.setAttribute('aria-pressed', String(selected)); button.setAttribute('aria-label', selected ? name.replace('Сохранить','Убрать') : name); const toast=document.getElementById('db-toast'); toast.textContent=selected?'Сохранено в образце до перезагрузки.':'Убрано из сохранённого.'; setTimeout(()=>{toast.textContent='';},3500); });
  });
  syncBudget(); updateDate(); updateSummary();
})();
