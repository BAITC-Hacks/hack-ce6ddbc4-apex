# Фаза 4 — заметки для слияния

Ветка `claude/phase-4-implementation-6a1f79` собрана параллельно с фазами 1–3 от общего коммита `fbd1f82`. Спецификация — `docs/PHASE_4_MATCHING_ENGINE.md` (на момент сборки не закоммичена в `main`). Этот файл перечисляет, что внутри ветки, где она сознательно отходит от спецификации и что сделать при соединении с остальными фазами.

## 1. Что внутри

| Слой | Файлы |
| --- | --- |
| Движок (чистый Python) | `matcher/models.py`, `validation.py`, `filters.py`, `scoring.py`, `explain.py`, `engine.py` |
| API | `app/routes/api.py`: `POST /api/recommend` (`RecommendIn` → `SearchResponse`, пример S1 в Swagger) |
| Веб-адаптер `/app` | `app/search.py` (разбор query, состояния, демо-сценарии, `search_context()`, заглушка `record_search()`) |
| Маршрут | `app/routes/pages.py`: `/app` вызывает `search_context()`; заглушки `/login`, `/register` не тронуты |
| Шаблоны (только новые файлы) | `app/search.html`, `partials/search_form.html`, `search_results.html`, `status_banner.html`, `result_card.html`, `funnel.html`, `whynot.html` |
| Стили и скрипт | `app/static/css/search.css`, `app/static/js/search.js` (подключены из `app/search.html`, `base.html` не менялся) |
| Тексты | Новые ключи одним блоком в конце `ru.json`, `kk.json`, `en.json`; существующие ключи не изменялись |
| Тесты и инструменты | `tests/test_engine_dod.py`, `tests/test_search_page.py`, минимальная правка `tests/test_pages.py`; `scripts/find_demo_queries.py` |

## 2. Отличия от `PHASE_4_MATCHING_ENGINE.md` и причины

Спецификация фазы 1 и дизайнбук новее и имеют приоритет (мастер-план, «Текущий этап»).

| Спецификация фазы 4 | В ветке | Источник решения |
| --- | --- | --- |
| Поле «Пожелания» в GET-форме `/app`, `wishes` в `to_query()` | Поля нет в форме и URL; `wishes` принимает только JSON `POST /api/recommend` | Фаза 1 §10.1, мастер-план: пожелания не передаются в URL |
| Бюджет: мусор → 0 → «больше 0 ₸» | `matcher.validation.normalize_budget()` по правилам фазы 1: пробелы, NBSP, узкий NBSP; коды `positive`, `integer`, `too_large`; предел `BUDGET_MAX = 9 007 199 254 740 991` проверяет и `validate()` | Фаза 1 §9.6, §22: один источник правил в доменном слое |
| Любой параметр запускает подбор | Неполный набор из пяти обязательных полей только предзаполняет форму, без баннера и без вызова движка | Мастер-план: частичные параметры без фиктивного результата; фаза 1 §10.4 |
| — | Повтор базового параметра (`city=A&city=B`) — ошибка поля `duplicate` | Фаза 1 §10.4 |
| `explain.duration.unbounded`: «работа не привязана к часам» | «лимит по часам в каталоге не указан»; в карточке — «Длительность в каталоге не указана» | Фаза 1 §22, дизайнбук §8.3 |
| Заголовки статусов «Подобрали», «Подобрали меньше трёх» … | Заголовки дизайнбука §8.4: «Подобрали 3 варианта», «Подобрали 2 варианта / 1 вариант», … | Дизайнбук |
| `partials/card.html` | `partials/result_card.html` — `card.html` уже занят карточкой лендинга | Конфликт имён |
| `git rm app/templates/app/placeholder.html` | Файл сохранён: им пользуются заглушки входа | Фаза 1 §17 |
| CSS в конец `app.css` | Отдельный `search.css` | Меньше конфликтов при слиянии |
| Тесты `/app` в `test_pages.py` | Отдельный `tests/test_search_page.py`; проверка плашки гостя отложена до фазы 3 | Меньше конфликтов при слиянии |
| Демо-ссылки = чистые параметры запроса | Добавлен маркер `demo=<ключ>`; страница показывает, что открыт пример | Фаза 1 §22: демо-сценарий не подменяет черновик пользователя |
| Сигнатура `recommend(catalog, req, tr)` | Без изменений; добавлена публичная `invalid_response(req, errors, tr)` для ошибок разбора веб-формы | Ошибки разбора и доменные ошибки в одном баннере |

## 3. Соединение с фазой 1 (гостевой бриф)

Фаза 1 в рабочей копии `main` заменяет `/app` на `guest_request()` + `app/request.html` + `app/brief.py`. Обе ветки меняют обработчик `/app` — конфликт гарантирован и решается так:

1. Оставить один обработчик `/app`. Основа — `search_context(request)` из `app/search.py`; сводку условий фазы 1 (`request.html`, ссылки «Изменить» на `/#brief-<поле>`) показывать над формой или вместо неё, когда `state == "prefill"` или `"empty"`.
2. `app/brief.py`: `normalize_budget()` делегировать в `matcher.validation.normalize_budget()` (правила совпадают дословно), `BUDGET_MAX` импортировать оттуда же. `Brief.normalized(lang)` совместим с `SearchRequest(**…)`.
3. `static/js/brief.js`: не сохранять черновик, если в URL есть `demo=`.
4. Лендинг: CTA «Подбор без регистрации», блок `/app` и FAQ меняются одновременно с подключением поиска (фаза 1 §22). Фраза «до трёх» остаётся.
5. `ru.json`/`kk.json`/`en.json`: при конфликте взять объединение ключей. Фаза 1 удаляет старые `search.preview.*` и `demo.month` … — ветка фазы 4 их не использует. Новые префиксы фазы 4: `form.*`, `search.summary|why|score|…`, `status.<статус>.title`, `reason.group|detail.*`, `explain.*`, `funnel.*`, `demo.s*`, `result.*`.
6. `tests/test_pages.py`: в тесте заглушек `/app` больше не участвует.

## 4. Соединение с фазами 2–3 (аккаунты)

- `app/search.py` импортирует `get_current_user` из `app/deps.py`, а пока файла нет — берёт `request.state.user`. После слияния шим можно удалить.
- `app/search.html` включает `partials/guest_banner.html` с `ignore missing` первой строкой контента — плашка фазы 3 появится сама. После слияния вернуть проверку `guest-banner` в тест `/app`.
- Вошедшему без `city` в query форма подставляет `preferred_city` уже после подбора: ссылка на выдачу воспроизводима у гостя и у вошедшего.

## 5. Для фаз 5–6

Точки расширения — раздел 17 спецификации без изменений: `ATOM_WEIGHTS`/`build_atoms()`, `contrast_atoms()`, `scoring.COMPONENTS`/`WEIGHTS`, `SearchResponse.hints`, `record_search()` в `app/search.py` (запись в `searches` — фаза 6). Фаза 5 строится поверх `matcher/` этой ветки: её стоит начинать от этой ветки, а не от `fbd1f82`, иначе те же файлы будут написаны дважды.
