'use strict';
// Guest brief: tab-local draft, URL snapshot, live event card and client checks.
// The server repeats every check in app/brief.py; this script only improves the form.
(() => {
  const FIELDS = ['city', 'date', 'event_type', 'category', 'budget'];
  const STORAGE_LIMIT = 16 * 1024;
  const SPACES = [' ', String.fromCharCode(0xa0), String.fromCharCode(0x202f)];
  const NBSP = String.fromCharCode(0xa0);
  const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const getStorage = () => {
    try { return window.sessionStorage; } catch (error) { return null; }
  };
  const emptyValues = () => Object.fromEntries(FIELDS.map((name) => [name, '']));
  const hasValues = (values) => FIELDS.some((name) => values[name] !== '');

  const readDraft = (key) => {
    let raw = null;
    try {
      const storage = getStorage();
      raw = storage ? storage.getItem(key) : null;
    } catch (error) {
      return null;
    }
    if (typeof raw !== 'string' || raw === '' || raw.length > STORAGE_LIMIT) return null;
    let data;
    try { data = JSON.parse(raw); } catch (error) { return null; }
    if (!data || typeof data !== 'object' || Array.isArray(data) || data.version !== 1) return null;
    const source = data.values;
    if (!source || typeof source !== 'object' || Array.isArray(source)) return null;
    const values = emptyValues();
    for (const name of FIELDS) {
      if (!Object.prototype.hasOwnProperty.call(source, name)) continue;
      if (typeof source[name] !== 'string') return null;
      values[name] = source[name];
    }
    return values;
  };

  const writeDraft = (key, values) => {
    try {
      const storage = getStorage();
      if (!storage) return false;
      const record = { version: 1, values: {}, updated_at: new Date().toISOString() };
      FIELDS.forEach((name) => { record.values[name] = values[name] || ''; });
      storage.setItem(key, JSON.stringify(record));
      return true;
    } catch (error) {
      return false;
    }
  };

  const removeDraft = (key) => {
    try {
      const storage = getStorage();
      if (storage) storage.removeItem(key);
      return true;
    } catch (error) {
      return false;
    }
  };

  // Explicit base parameters in the address form one snapshot; nothing is merged into it.
  const urlSnapshot = () => {
    const params = new URLSearchParams(window.location.search);
    if (!FIELDS.some((name) => params.has(name))) return null;
    const values = emptyValues();
    const duplicates = [];
    FIELDS.forEach((name) => {
      const all = params.getAll(name);
      if (all.length > 1) duplicates.push(name);
      else if (all.length === 1) values[name] = all[0];
    });
    return { values, duplicates };
  };

  const addressWith = (values) => {
    const current = new URLSearchParams(window.location.search);
    const params = new URLSearchParams();
    if (values) FIELDS.forEach((name) => params.append(name, values[name]));
    if (current.has('lang')) params.set('lang', current.get('lang'));
    const query = params.toString();
    return window.location.pathname + (query ? `?${query}` : '') + window.location.hash;
  };

  const updateLanguageLinks = () => {
    const params = new URLSearchParams(window.location.search);
    params.delete('lang');
    const query = params.toString();
    const next = window.location.pathname + (query ? `?${query}` : '') + window.location.hash;
    document.querySelectorAll('[data-lang-link]').forEach((link) => {
      link.setAttribute('href', `/lang/${link.dataset.langLink}?next=${encodeURIComponent(next)}`);
    });
  };

  // ---------- /app: restore once, then keep the draft equal to the checked summary ----------
  const request = document.querySelector('[data-request]');
  if (request) {
    const key = request.dataset.storageKey;
    const syncRequest = () => {
      const snapshot = urlSnapshot();
      if (!snapshot) {
        const draft = readDraft(key);
        if (draft && hasValues(draft)) {
          const params = new URLSearchParams();
          FIELDS.forEach((name) => { if (draft[name] !== '') params.append(name, draft[name]); });
          const lang = new URLSearchParams(window.location.search).get('lang');
          if (lang) params.set('lang', lang);
          window.location.replace(`/app?${params.toString()}`);
        }
        return;
      }
      const note = request.querySelector('[data-storage-note]');
      if (note) note.hidden = writeDraft(key, snapshot.values);
    };
    syncRequest();
    window.addEventListener('pageshow', (event) => { if (event.persisted) syncRequest(); });
    return;
  }

  // ---------- landing brief ----------
  const form = document.querySelector('[data-brief-form]');
  const configNode = document.getElementById('brief-config');
  if (!form || !configNode) return;
  const config = JSON.parse(configNode.textContent);
  const text = config.text;
  const key = config.storageKey;
  const format = (template, params) => String(template).replace(/\{(\w+)\}/g, (match, name) => (
    Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : match
  ));
  const capitalize = (value) => value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
  const groupDigits = (digits, separator) => digits.replace(/\B(?=(\d{3})+(?!\d))/g, separator);
  const formatKzt = (value) => `${groupDigits(String(value), NBSP)}${NBSP}₸`;

  const controls = {
    city: [...form.querySelectorAll('input[name="city"]')],
    date: form.querySelector('#brief-date'),
    event_type: [...form.querySelectorAll('input[name="event_type"]')],
    category: form.querySelector('#brief-category'),
    budget: form.querySelector('#brief-budget'),
  };
  const heading = document.getElementById('brief-heading');
  const summary = document.querySelector('[data-error-summary]');
  const summaryList = summary.querySelector('[data-error-list]');
  const message = form.querySelector('[data-brief-message]');
  const storageNote = form.querySelector('[data-storage-note]');
  const draftStatus = document.querySelector('[data-draft-status]');
  const announcer = document.querySelector('[data-card-announce]');
  const card = document.querySelector('[data-event-card]');
  const presets = document.querySelector('[data-budget-presets]');
  const replaceDialog = document.getElementById('replace-dialog');
  const clearDialog = document.getElementById('clear-dialog');
  const catalog = document.querySelector('[data-catalog]');

  let attempted = false;
  let dirty = false;
  let pendingDate = false;
  let announceTimer;
  const shown = {};

  // ---- rules mirrored from app/brief.py ----
  const checkBudget = (raw) => {
    let compact = raw;
    SPACES.forEach((space) => { compact = compact.split(space).join(''); });
    if (compact === '') return { value: null, error: null };
    if (/^-[0-9]+$/.test(compact)) return { value: null, error: 'brief.budget.positive' };
    if (!/^[0-9]+$/.test(compact)) return { value: null, error: 'brief.budget.integer' };
    const digits = compact.replace(/^0+/, '') || '0';
    const max = config.budgetMax;
    if (digits.length > max.length || (digits.length === max.length && digits > max)) {
      return { value: null, error: 'brief.budget.too_large' };
    }
    const value = Number(digits);
    if (value <= 0) return { value: null, error: 'brief.budget.positive' };
    return { value, error: null };
  };

  const parseIsoDate = (raw) => {
    if (!/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(raw)) return null;
    const [year, month, day] = raw.split('-').map(Number);
    if (year < 1) return null;
    const date = new Date(0);
    date.setUTCFullYear(year, month - 1, day);
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
    return { year, month, day, weekday: (date.getUTCDay() + 6) % 7 };
  };

  const check = (name, raw) => {
    if (name === 'budget') return checkBudget(raw);
    if (name === 'date') {
      if (raw === '') {
        const bad = controls.date.validity && controls.date.validity.badInput;
        return { value: null, error: bad ? 'brief.date.invalid' : null };
      }
      if (!parseIsoDate(raw)) return { value: null, error: 'brief.date.invalid' };
      if (raw < config.window.start || raw > config.window.end) return { value: null, error: 'brief.date.window' };
      return { value: raw, error: null };
    }
    if (raw === '') return { value: null, error: null };
    const allowed = { city: config.cities, event_type: config.formats, category: config.categories }[name];
    if (allowed.includes(raw)) return { value: raw, error: null };
    return { value: null, error: { city: 'brief.city.unknown', event_type: 'brief.event_type.unknown', category: 'brief.category.error' }[name] };
  };

  const missingError = {
    city: 'brief.city.error', date: 'brief.date.error', event_type: 'brief.event_type.error',
    category: 'brief.category.error', budget: 'brief.budget.error',
  };

  // ---- DOM values ----
  const checkedValue = (name) => {
    const checked = controls[name].find((input) => input.checked);
    return checked ? checked.value : '';
  };
  const rawValues = () => ({
    city: checkedValue('city'),
    date: controls.date.value,
    event_type: checkedValue('event_type'),
    category: controls.category.value,
    budget: controls.budget.value,
  });
  const canonicalValues = () => {
    const raw = rawValues();
    const budget = checkBudget(raw.budget);
    let compact = raw.budget;
    SPACES.forEach((space) => { compact = compact.split(space).join(''); });
    raw.budget = budget.value !== null ? String(budget.value) : (compact === '' ? '' : raw.budget);
    return raw;
  };
  const results = () => {
    const raw = rawValues();
    return Object.fromEntries(FIELDS.map((name) => [name, check(name, raw[name])]));
  };

  const setValues = (values) => {
    ['city', 'event_type'].forEach((name) => {
      controls[name].forEach((input) => { input.checked = input.value === values[name]; });
    });
    controls.date.value = values.date;
    const hasOption = [...controls.category.options].some((option) => option.value === values.category);
    controls.category.value = hasOption ? values.category : '';
    const budget = checkBudget(values.budget);
    controls.budget.value = budget.value !== null ? groupDigits(String(budget.value), ' ') : values.budget;
  };

  // ---- errors ----
  const focusControl = (name) => {
    const control = Array.isArray(controls[name])
      ? (controls[name].find((input) => input.checked) || controls[name][0])
      : controls[name];
    const field = (Array.isArray(controls[name]) ? document.getElementById(`brief-${name}`) : control.closest('.tl-field')) || control;
    field.scrollIntoView({ block: 'center', behavior: reduceMotion() ? 'auto' : 'smooth' });
    control.focus({ preventScroll: true });
  };

  const setError = (name, errorKey) => {
    const node = form.querySelector(`[data-error-for="${name}"]`);
    const targets = Array.isArray(controls[name]) ? controls[name] : [controls[name]];
    if (errorKey) {
      node.querySelector('span').textContent = text[errorKey] || errorKey;
      node.hidden = false;
      targets.forEach((target) => target.setAttribute('aria-invalid', 'true'));
      shown[name] = errorKey;
    } else {
      node.querySelector('span').textContent = '';
      node.hidden = true;
      targets.forEach((target) => target.removeAttribute('aria-invalid'));
      delete shown[name];
    }
  };

  const errorFor = (name, result) => result.error || (result.value === null ? missingError[name] : null);

  const renderSummary = () => {
    const names = FIELDS.filter((name) => shown[name]);
    summaryList.replaceChildren(...names.map((name) => {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = `#brief-${name}`;
      link.dataset.errorLink = name;
      const own = form.querySelector(`[data-error-for="${name}"] span`).textContent;
      link.textContent = `${config.fieldLabels[name]}. ${text[shown[name]] || own}`;
      item.append(link);
      return item;
    }));
    summary.hidden = names.length === 0;
  };

  const validateField = (name) => {
    const result = check(name, rawValues()[name]);
    setError(name, errorFor(name, result));
    if (!summary.hidden || attempted) renderSummary();
  };

  // ---- event card, coverage, presets ----
  const cardField = (name) => card && card.querySelector(`[data-card-field="${name}"]`);
  const cardText = (name, result) => {
    if (result.value === null) return text[`landing.event_card.${name}_empty`];
    if (name === 'city' || name === 'category') return config.labels[name][result.value];
    if (name === 'event_type') return capitalize(config.labels.event_type[result.value]);
    if (name === 'budget') return format(text['landing.event_card.budget_value'], { amount: formatKzt(result.value) });
    const parts = parseIsoDate(result.value);
    return format(text['date.full'], { day: parts.day, month: config.monthsGenitive[parts.month - 1], year: parts.year });
  };

  const renderCard = (state) => {
    const filled = FIELDS.filter((name) => state[name].value !== null).length;
    if (card) {
      ['city', 'event_type', 'category', 'budget'].forEach((name) => {
        const node = cardField(name);
        node.textContent = cardText(name, state[name]);
        node.classList.toggle('is-empty', state[name].value === null);
      });
      const dateBox = card.querySelector('[data-card-date]');
      const parts = state.date.value ? parseIsoDate(state.date.value) : null;
      dateBox.classList.toggle('is-empty', !parts);
      const day = dateBox.querySelector('[data-card-part="day"]');
      day.hidden = !parts;
      day.textContent = parts ? String(parts.day) : '';
      dateBox.querySelector('[data-card-part="month"]').textContent = parts ? config.months[parts.month - 1] : text['landing.event_card.date_empty'];
      dateBox.querySelector('[data-card-part="year"]').textContent = parts ? String(parts.year) : '';
      dateBox.querySelector('[data-card-part="weekday"]').textContent = parts ? config.weekdays[parts.weekday] : '';
      card.querySelector('[data-card-progress]').textContent = format(text['landing.event_card.progress'], { n: filled });
      card.querySelectorAll('.tl-progress-track i').forEach((segment, index) => segment.classList.toggle('is-on', index < filled));
    }
    const stamp = form.querySelector('[data-date-stamp]');
    const parts = state.date.value ? parseIsoDate(state.date.value) : null;
    stamp.classList.toggle('is-empty', !parts);
    stamp.querySelector('[data-stamp-day]').textContent = parts ? String(parts.day) : '';
    stamp.querySelector('[data-stamp-month]').textContent = parts ? config.monthsShort[parts.month - 1] : '';
    const coverage = form.querySelector('[data-coverage]');
    const category = state.category.value;
    const city = state.city.value;
    if (category && city) {
      const count = (config.counts[category] || {})[city] || 0;
      coverage.textContent = count ? format(text['brief.category.coverage'], { n: count }) : text['brief.category.coverage_zero'];
    } else if (category) {
      coverage.textContent = text['brief.category.coverage_city'];
    } else {
      coverage.textContent = format(text['brief.category.help_empty'], { n: config.categories.length });
    }
    presets.querySelectorAll('[data-budget]').forEach((button) => {
      button.setAttribute('aria-pressed', String(state.budget.value !== null && String(state.budget.value) === button.dataset.budget));
    });
    return filled;
  };

  const announce = (name) => {
    clearTimeout(announceTimer);
    announceTimer = setTimeout(() => {
      const state = results();
      const filled = FIELDS.filter((field) => state[field].value !== null).length;
      announcer.textContent = format(text['landing.event_card.announce'], {
        field: config.fieldLabels[name],
        value: cardText(name, state[name]),
        progress: format(text['landing.event_card.progress'], { n: filled }),
      });
    }, 600);
  };

  const say = (key, params) => { message.textContent = format(text[key], params || {}); };
  const clearMessage = () => { message.textContent = ''; };

  // ---- catalog overview follows the brief location ----
  const catalogRadios = catalog ? [...catalog.querySelectorAll('input[name="catalog_city"]')] : [];
  const renderCatalog = (city) => {
    if (!catalog) return;
    catalogRadios.forEach((input) => { input.checked = input.value === city; });
    catalog.querySelectorAll('[data-category]').forEach((row) => {
      const name = row.dataset.category;
      const count = city ? ((config.counts[name] || {})[city] || 0) : config.totals[name];
      row.querySelector('[data-count]').textContent = String(count);
      row.querySelector('[data-zero]').hidden = count !== 0;
    });
    catalog.querySelector('[data-catalog-caption]').textContent = city
      ? format(text['landing.catalog.caption_city'], { city: config.labels.city[city] })
      : text['landing.catalog.caption_all'];
  };

  // ---- persistence ----
  const showStorage = (saved) => { storageNote.hidden = saved; };
  const persist = () => {
    dirty = true;
    const values = canonicalValues();
    showStorage(writeDraft(key, values));
    window.history.replaceState(window.history.state, '', addressWith(hasValues(values) ? values : null));
    updateLanguageLinks();
  };

  const commit = (name) => {
    clearMessage();
    const state = results();
    renderCard(state);
    if (name === 'budget' && state.budget.value !== null) {
      controls.budget.value = groupDigits(String(state.budget.value), ' ');
    }
    if (name === 'city') renderCatalog(state.city.value || '');
    validateField(name);
    persist();
    announce(name);
  };

  const applyValues = (values) => {
    setValues(values);
    FIELDS.forEach((name) => setError(name, null));
    summary.hidden = true;
    const state = results();
    renderCard(state);
    renderCatalog(state.city.value || '');
  };

  // ---- dialogs ----
  // Settles on the button or Escape directly, so it never waits for a render-timed event.
  const confirmWith = (dialog, trigger) => new Promise((resolve) => {
    if (!dialog || typeof dialog.showModal !== 'function') {
      resolve(window.confirm(dialog ? dialog.querySelector('h2').textContent : ''));
      return;
    }
    let settled = false;
    const finish = (confirmed) => {
      if (settled) return;
      settled = true;
      dialog.removeEventListener('click', onClick);
      dialog.removeEventListener('cancel', onCancel);
      dialog.removeEventListener('close', onClose);
      if (dialog.open) dialog.close(confirmed ? 'confirm' : 'cancel');
      if (!confirmed && trigger && document.contains(trigger)) trigger.focus();
      resolve(confirmed);
    };
    const onClick = (event) => {
      const button = event.target.closest('button[value]');
      if (!button) return;
      event.preventDefault();
      finish(button.value === 'confirm');
    };
    const onCancel = (event) => {
      event.preventDefault();
      finish(false);
    };
    const onClose = () => finish(dialog.returnValue === 'confirm');
    dialog.addEventListener('click', onClick);
    dialog.addEventListener('cancel', onCancel);
    dialog.addEventListener('close', onClose);
    dialog.returnValue = '';
    dialog.showModal();
  });

  const fillExample = async (trigger, moveToForm) => {
    const current = canonicalValues();
    const differs = FIELDS.some((name) => current[name] !== '' && current[name] !== config.example[name]);
    if (differs && !(await confirmWith(replaceDialog, trigger))) return;
    attempted = false;
    applyValues(config.example);
    persist();
    draftStatus.hidden = true;
    say('brief.draft.example_filled');
    if (moveToForm) {
      document.getElementById('brief').scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth' });
      heading.focus({ preventScroll: true });
    }
  };

  const clearBrief = async (trigger) => {
    const hadDraft = readDraft(key) !== null;
    if ((hasValues(canonicalValues()) || hadDraft) && !(await confirmWith(clearDialog, trigger))) return;
    attempted = false;
    applyValues(emptyValues());
    removeDraft(key);
    dirty = true;
    window.history.replaceState(window.history.state, '', addressWith(null));
    updateLanguageLinks();
    draftStatus.hidden = true;
    say('brief.draft.cleared');
    heading.focus({ preventScroll: true });
    heading.scrollIntoView({ block: 'start', behavior: reduceMotion() ? 'auto' : 'smooth' });
  };

  // ---- initial state: URL snapshot, then tab draft, then empty ----
  const initialise = (fromPageShow) => {
    const snapshot = urlSnapshot();
    let restored = false;
    if (snapshot) {
      setValues(snapshot.values);
      if (fromPageShow) {
        FIELDS.forEach((name) => { if (shown[name]) validateField(name); });
      }
    } else {
      const draft = readDraft(key);
      if (draft && hasValues(draft)) {
        setValues(draft);
        restored = true;
      }
    }
    const state = results();
    renderCard(state);
    if (state.city.value) renderCatalog(state.city.value);
    if (snapshot && !dirty) {
      // Keep an explicit link as it was typed, so a refresh still shows its errors.
      const values = { ...snapshot.values };
      snapshot.duplicates.forEach((name) => { values[name] = ''; });
      showStorage(writeDraft(key, values));
      updateLanguageLinks();
    } else if (snapshot || restored) {
      persist();
    } else {
      updateLanguageLinks();
    }
    if (restored && !fromPageShow) draftStatus.hidden = false;
  };

  draftStatus.hidden = true;
  // Server-rendered errors of an explicit link stay visible until the field changes.
  form.querySelectorAll('[data-error-for]').forEach((node) => {
    if (!node.hidden) shown[node.dataset.errorFor] = node.dataset.errorKey || missingError[node.dataset.errorFor];
  });
  initialise(false);

  const hashField = FIELDS.find((name) => window.location.hash === `#brief-${name}`);
  if (hashField) {
    window.setTimeout(() => focusControl(hashField), 0);
  }

  // ---- events ----
  form.addEventListener('change', (event) => {
    const name = event.target.name;
    if (!FIELDS.includes(name)) return;
    if (event.target === controls.date && document.activeElement === controls.date && !attempted) {
      pendingDate = true;
      const state = results();
      renderCard(state);
      if (shown.date && !errorFor('date', state.date)) validateField('date');
      return;
    }
    pendingDate = false;
    commit(name);
  });
  controls.date.addEventListener('blur', () => {
    if (!pendingDate) return;
    pendingDate = false;
    commit('date');
  });
  controls.budget.addEventListener('input', () => {
    clearMessage();
    const state = results();
    renderCard(state);
    if (shown.budget && state.budget.value !== null) validateField('budget');
  });
  presets.addEventListener('click', (event) => {
    const button = event.target.closest('[data-budget]');
    if (!button) return;
    controls.budget.value = groupDigits(button.dataset.budget, ' ');
    commit('budget');
  });
  form.addEventListener('submit', (event) => {
    attempted = true;
    const state = results();
    FIELDS.forEach((name) => setError(name, errorFor(name, state[name])));
    renderSummary();
    if (!summary.hidden) {
      event.preventDefault();
      summary.focus();
      summary.scrollIntoView({ block: 'center', behavior: reduceMotion() ? 'auto' : 'smooth' });
      return;
    }
    controls.budget.value = String(state.budget.value);
    persist();
  });
  summary.addEventListener('click', (event) => {
    const link = event.target.closest('[data-error-link]');
    if (!link) return;
    event.preventDefault();
    focusControl(link.dataset.errorLink);
  });
  document.querySelectorAll('[data-brief-clear]').forEach((button) => {
    button.addEventListener('click', () => clearBrief(button));
  });
  document.querySelectorAll('[data-brief-example]').forEach((button) => {
    button.addEventListener('click', () => fillExample(button, false));
  });
  document.querySelectorAll('[data-fill-example]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      fillExample(link, true);
    });
  });
  document.querySelectorAll('[data-lang-link]').forEach((link) => {
    link.addEventListener('click', () => { if (dirty || pendingDate) persist(); });
  });
  if (catalog) {
    catalog.addEventListener('change', (event) => {
      if (event.target.name !== 'catalog_city') return;
      const city = event.target.value;
      renderCatalog(city);
      if (city) {
        controls.city.forEach((input) => { input.checked = input.value === city; });
        commit('city');
      }
    });
    catalog.addEventListener('click', (event) => {
      const row = event.target.closest('[data-category]');
      if (!row) return;
      event.preventDefault();
      controls.category.value = row.dataset.category;
      commit('category');
      say('brief.draft.category_selected', { category: config.labels.category[row.dataset.category] });
      focusControl('category');
    });
  }
  window.addEventListener('pageshow', (event) => {
    if (event.persisted) initialise(true);
  });
  // Same-document Back/Forward between section anchors restores an older address;
  // write the current form back into it so a refresh cannot revert the edits.
  window.addEventListener('popstate', () => { if (dirty) persist(); });

  // JavaScript-only controls appear only after every listener is attached.
  document.querySelectorAll('[data-brief-example], [data-brief-clear], [data-budget-presets], [data-catalog-switch]')
    .forEach((node) => { node.hidden = false; });
})();
