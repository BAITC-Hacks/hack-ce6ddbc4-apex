# Tandau — мастер-план на хакатон HackAlem AI (трек 06 «Креативные индустрии», кейс Firebird)

> **Tandau** (таңдау — «выбор») — сервис, который по параметрам заказа выдаёт до 3 event-подрядчиков и честно объясняет, почему именно они, а если подобрать нельзя — почему и что изменить.
>
> Этот файл хранит общий план команды: стек, структура репозитория, маршруты, схема БД, i18n, контракты API, тайминг 7 фаз и правила сдачи. Детали каждой фазы — в `docs/PHASE_1..7_*.md`. Задача для второго участника — `docs/ISSUE_i18n_and_minor_tasks.md`. Все факты о данных и правилах — `docs/01_REFERENCE.md`.

---

## Текущий этап

**Завершена фаза 0. Фаза 1 ещё не принята.** Фаза 0 включает техническую основу, каталог, дизайнбук и полноразмерный макет. Макет не означает работающий подбор, авторизацию или готовый основной лендинг.

[Новая спецификация фазы 1](PHASE_1_FOUNDATION_AND_LANDING.md) заменяет прежний план фундамента и лендинга. Она задаёт перенос утверждённого дизайна на `/`, пять условий события, гостевой черновик и просмотр условий на `/app`. Подбор остаётся в фазе 4. Новая спецификация имеет приоритет над старым расписанием, визуальными фрагментами и инструкциями полной замены файлов в последующих фазах.

| Фаза | Статус и граница |
| --- | --- |
| 0 | Завершена. Основа и утверждённые макеты |
| 1 | Спецификация готова. Основной лендинг, бриф и гостевой просмотр условий |
| 2 | Запланирована. Регистрация |
| 3 | Запланирована. Вход и сессии |
| 4 | Запланирована. Движок и реальные результаты на `/app` |
| 5 | Запланирована. Вычисляемые объяснения и сравнение дат |
| 6 | Запланирована. Кабинет, история, постоянное избранное |
| 7 | Запланирована. Проверка целого продукта и сдача |

Часы ниже являются исходным расписанием хакатона, а не актуальной оценкой разработки и не подтверждением завершения этапов. Текущие незакоммиченные изменения проверяются отдельно; статус фазы меняется после приёмки.

Новые контракты фазы 1 сохраняются дальше. Черновик находится в sessionStorage отдельно от очищаемой auth-сессии. URL использует `budget`, будущая модель использует `budget_kzt`. Пожелания не передаются в URL. Частичные параметры `/app` предзаполняют запрос без фиктивного результата. Постоянная история и избранное остаются фазой 6.

## 0. Исходные условия хакатона

| Что | Значение |
| --- | --- |
| Соревновательная часть | **23.09.2026, 13:00–18:00** (Астана). Что лежит в репозитории на 18:00 — финальная версия |
| Дисквалификация | Нет коммита/прогресса **в любом часовом окне** (13–14, 14–15, 15–16, 16–17, 17–18) |
| Недопуск без апелляции | Эксперт не смог запустить проект **по README** |
| Проверка без личных аккаунтов | Ключевой сценарий должен работать **без регистрации** (гостевой режим) и/или с **демо-аккаунтом из README** (п. 5.6.6) |
| Репозиторий | Только командный GitHub-репозиторий, созданный платформой edu.astanahub.com |
| Приоритет жюри кейса | качество объяснений > честная обработка редких/занятых/пустых > скорость > интерфейс |
| Критерии (100) | Соответствие ТЗ 25 · Техническая реализация 25 · README и воспроизводимость 25 · Ценность 15 · Потенциал и оригинальность 10 |
| Роли | **Главный разработчик** — фазы 1–7 (весь основной код). **Участник 2** — issue: тримовность RU/KZ/EN + мелкие задачи |
| AI-агент для разработки | Codex (обязательное условие организаторов — использовать AI-агента). Каждый документ фазы содержит готовые промпты |

**Правило отсечения.** Если отстаём от графика — режем в таком порядке: фаза 6 (кабинет) → LLM-слой фазы 5 → визуальные украшения лендинга. **Никогда не режем** фазы 4, 5 (ядро объяснений) и 7 (README, тесты, сдача): на них 75 из 100 баллов.

---

## 1. Исходное расписание семи фаз

| # | Фаза | Время | Что на выходе | Коммит(ы) | Часовое окно |
| --- | --- | --- | --- | --- | --- |
| 1 | Фундамент + лендинг | 14:10–14:50 | Каркас FastAPI, дизайн-система, i18n-каркас, загрузка данных (66), лендинг с живой статистикой | 14:30 `feat: skeleton`, 14:50 `feat: landing` | 14–15 ✅ |
| 2 | Регистрация | 14:50–15:10 | SQLite, таблица users, scrypt-хэш, форма регистрации с валидацией, CSRF, авто-вход | 15:10 `feat: registration` | 15–16 ✅ |
| 3 | Вход, сессии, доступ | 15:10–15:30 | Login/logout, сессии, гостевой режим, демо-аккаунт, защищённые маршруты | 15:30 `feat: login & sessions` | 15–16 ✅ |
| 4 | Движок подбора | 15:30–16:20 | `matcher/`: фильтры с причинами, 5 статусов, скоринг, шаблонные объяснения, `/api/recommend`, страница `/app` | 15:55 `wip: engine`, 16:20 `feat: matching engine` | 15–16 ✅, 16–17 ✅ |
| 5 | Объяснения и честность | 16:20–16:55 | Факты из описаний, цитаты (TF-IDF), контрастные объяснения, «почему не больше», подсказки, сравнение дат, (опц.) LLM-редактор | 16:55 `feat: explanations` | 16–17 ✅ |
| 6 | Личный кабинет | 16:55–17:15 | История запросов, избранное, профиль подрядчика с календарём | 17:15 `feat: account` | 17–18 ✅ |
| 7 | Качество и сдача | 17:15–17:45 | pytest DoD, README, чистый клон, фриз 17:30, финальный push 17:40, «Сдать решение» | 17:40 `release: v1.0` | 17–18 ✅ |
| — | Резерв | 17:45–18:00 | Ничего не трогаем. Проверяем GitHub и форму сдачи | — | — |

Участник 2 работает параллельно всё время (issue): коммитит свои файлы `app/i18n/*.json`, `static/img/*`, скриншоты, раздел README «Языки».

**Будильники:** 14:45, 15:45, 16:45, 17:35 — «есть ли пуш в этом часе?».

---

## 2. Стек (фиксируем, не обсуждаем)

| Слой | Выбор | Почему |
| --- | --- | --- |
| Язык | Python 3.10+ | Есть у экспертов, у нас 3.10.12 |
| Веб | FastAPI + Uvicorn | API + Swagger `/docs` бесплатно, один процесс |
| Страницы | Jinja2 (серверный рендер) + ванильный JS | Без Node и сборки → README-гейт не страшен |
| Стили | Свой `static/css/app.css` на CSS-переменных | Без CDN: площадка может остаться без интернета |
| БД | SQLite через stdlib `sqlite3`, файл `var/tandau.db` | Ноль установки, создаётся на старте |
| Пароли | `hashlib.scrypt` (stdlib) + соль | Без bcrypt/passlib (проблемы установки на Windows) |
| Сессии | `starlette.middleware.sessions.SessionMiddleware` (itsdangerous) | Подписанная cookie, без Redis |
| Формы | `python-multipart` | Нужен FastAPI для `Form(...)` |
| Поиск по смыслу | Ручной TF-IDF по символьным n-граммам (stdlib) | Без numpy/sklearn, детерминированно, офлайн |
| LLM (опционально) | `openai` SDK, `LLM_MODE=off` по умолчанию | Ядро работает без ключа (п. 5.6.6) |
| Тесты | pytest + httpx (TestClient) | DoD-проверки автоматически |

`requirements.txt` (ставить именно так):

```text
fastapi>=0.110,<1.0
uvicorn>=0.27,<1.0
jinja2>=3.1,<4.0
python-multipart>=0.0.9
itsdangerous>=2.1,<3.0
pytest>=8.0,<9.0
httpx>=0.27,<0.28
```

`requirements-llm.txt` (только если включаем LLM):

```text
openai>=1.40,<2.0
```

---

## 3. Структура репозитория (контракт — не переименовывать)

```text
tandau/
├── run.py                         # python run.py → http://127.0.0.1:8000
├── requirements.txt
├── requirements-llm.txt
├── .env.example                   # SECRET_KEY, LLM_MODE, OPENAI_*, DATABASE_PATH
├── .gitignore                     # .env, var/, __pycache__/, .venv/, cache/
├── README.md
├── data/
│   ├── hackathon-dataset-anonymized.csv   # 66 строк, исходник организаторов
│   └── enriched.json                      # (фаза 5, опц.) факты из описаний, коммитим
├── matcher/                       # ЧИСТЫЙ Python, без веб-зависимостей
│   ├── __init__.py
│   ├── models.py                  # Contractor, SearchRequest, Card, Rejection, SearchResponse
│   ├── data.py                    # load_catalog() → Catalog (66), индексы
│   ├── filters.py                 # check(contractor, req) → list[Reason]
│   ├── scoring.py                 # score(contractor, req, ctx) → ScoreBreakdown
│   ├── facts.py                   # extract_facts(description) → Facts
│   ├── evidence.py                # TfidfIndex, best_quote(description, query)
│   ├── explain.py                 # build_atoms(), compose_explanation(), STOP_PHRASES
│   ├── hints.py                   # nearest_dates(), budget_hint(), other_city_hint()
│   ├── compare.py                 # compare_dates(req, date_a, date_b)
│   ├── llm.py                     # (опц.) rewrite_with_llm() + validate() + cache
│   └── engine.py                  # recommend(req) → SearchResponse
├── app/
│   ├── __init__.py
│   ├── main.py                    # create_app(): middleware, routers, static, startup
│   ├── config.py                  # Settings из env
│   ├── db.py                      # connect(), init_db(), seed_demo_user()
│   ├── security.py                # hash_password(), verify_password(), csrf
│   ├── i18n.py                    # load_locales(), t(), get_lang()
│   ├── deps.py                    # current_user(), require_user()
│   ├── routes/
│   │   ├── pages.py               # /, /app, /app/compare, /contractors/{id}
│   │   ├── auth.py                # /register, /login, /logout
│   │   ├── account.py             # /account/history, /account/shortlist
│   │   └── api.py                 # /api/meta, /api/recommend, /api/compare, /healthz
│   ├── i18n/
│   │   ├── ru.json                # ← Участник 2
│   │   ├── kk.json                # ← Участник 2
│   │   └── en.json                # ← Участник 2
│   ├── templates/
│   │   ├── base.html
│   │   ├── partials/{header,footer,flash,card,status_banner,funnel,lang_switch}.html
│   │   ├── landing.html
│   │   ├── auth/{register,login}.html
│   │   ├── app/{search,compare,contractor}.html
│   │   └── account/{history,shortlist}.html
│   └── static/
│       ├── css/app.css
│       ├── js/app.js
│       └── img/{logo.svg,favicon.svg}      # ← Участник 2
├── scripts/
│   ├── find_demo_queries.py       # печатает сильные демо-запросы по данным
│   └── enrich_llm.py              # (опц.) офлайн-обогащение описаний → data/enriched.json
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_auth.py
│   ├── test_engine_dod.py
│   └── test_pages.py
├── var/                           # создаётся на старте, в .gitignore
└── docs/                          # эти документы
```

Зона ответственности, чтобы не конфликтовать в git: **главный разработчик** — всё, кроме `app/i18n/*.json`, `app/static/img/*`, `docs/screenshots/*` и раздела README «Языки», которые ведёт **Участник 2**.

---

## 4. Маршруты (контракт)

### Страницы

| Метод | Путь | Доступ | Фаза | Что делает |
| --- | --- | --- | --- | --- |
| GET | `/` | все | 1 | Лендинг |
| GET | `/register` | гость | 2 | Форма регистрации |
| POST | `/register` | гость | 2 | Создать пользователя → авто-вход → `/app` |
| GET | `/login` | гость | 3 | Форма входа + кнопка «Войти как демо» |
| POST | `/login` | гость | 3 | Проверить пароль → сессия → `next` или `/app` |
| POST | `/logout` | вошедший | 3 | Очистить сессию → `/` |
| GET | `/app` | **все (гость тоже)** | 1 / 4 | Фаза 1 показывает гостевой черновик; фаза 4 добавляет подбор и результаты |
| GET | `/app/compare` | все | 5 | Тот же запрос на две даты, «вошёл/выпал» |
| GET | `/contractors/{id}` | все | 6 | Профиль подрядчика + календарь 100 дней |
| GET | `/account/history` | вошедший | 6 | Мои запросы (повторить в 1 клик) |
| GET | `/account/shortlist` | вошедший | 6 | Избранное |
| POST | `/account/shortlist/{id}` | вошедший | 6 | Добавить/убрать из избранного (toggle) |
| GET | `/lang/{code}` | все | 1 | Сменить язык (ru/kk/en) → назад |

### API (JSON, для экспертов и интеграции — всё видно в Swagger `/docs`)

| Метод | Путь | Фаза | Тело / ответ |
| --- | --- | --- | --- |
| GET | `/healthz` | 1 | `{"status":"ok","profiles":66}` |
| GET | `/api/meta` | 1 | города, категории (с количеством по городам), форматы, языки, окно дат |
| POST | `/api/recommend` | 4 | `SearchRequest` → `SearchResponse` |
| POST | `/api/compare` | 5 | `{request, date_a, date_b}` → `{a, b, diff}` |
| GET | `/api/contractors/{id}` | 6 | профиль + занятость |

Параметры страницы `/app` = поля `SearchRequest` в query-строке (`/app?city=Алматы&date=2026-10-17&event_type=свадьба&category=Ведущий&budget=1000000&language=казахский&duration=8`). Плюс: ссылку на выдачу можно отправить, повтор даёт тот же результат.

---

## 5. Схема БД (SQLite)

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  email           TEXT    NOT NULL UNIQUE,          -- хранить в lower()
  name            TEXT    NOT NULL,
  password_hash   TEXT    NOT NULL,                 -- scrypt$16384$8$1$<salt_hex>$<hash_hex>
  preferred_lang  TEXT    NOT NULL DEFAULT 'ru' CHECK (preferred_lang IN ('ru','kk','en')),
  preferred_city  TEXT,
  is_demo         INTEGER NOT NULL DEFAULT 0,
  created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS searches (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  params_json  TEXT    NOT NULL,        -- канонический JSON SearchRequest (sort_keys=True)
  status       TEXT    NOT NULL,        -- found|partial|no_category_in_city|none_match|invalid_request
  result_ids   TEXT    NOT NULL,        -- "HK-42352,HK-35215,HK-77838"
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_searches_user ON searches(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS shortlist (
  user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  contractor_id  TEXT    NOT NULL,
  created_at     TEXT    NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (user_id, contractor_id)
);
```

**Демо-аккаунт** (создаётся на старте, если нет; указан в README и на странице входа):
`demo@tandau.kz` / `Demo2026!` — `is_demo = 1`.

---

## 6. Авторизация и доступ (контракт)

- Сессия: `request.session["uid"]`, `request.session["csrf"]`. Cookie `tandau_session`, `max_age=7 дней`, `same_site="lax"`.
- `SECRET_KEY` из env; если не задан — генерируется при старте и пишется в `var/secret_key` (чтобы README не требовал ручной настройки).
- CSRF: каждая POST-форма содержит `<input type="hidden" name="csrf" value="{{ csrf }}">`; сервер сравнивает с сессией через `hmac.compare_digest`. JSON API (`/api/*`) — без CSRF (нет cookie-аутентификации для API).
- Гость может: лендинг, `/app`, `/app/compare`, `/contractors/{id}`, весь API. Вошедший дополнительно: история и избранное. **Подбор никогда не требует входа** — это закрывает п. 5.6.6.
- Защищённые страницы без сессии → `303` на `/login?next=<путь>`.
- Пароль: минимум 8 символов, хотя бы одна буква и одна цифра. Email — простая проверка `^[^@\s]+@[^@\s]+\.[^@\s]+$`, приводим к нижнему регистру.
- Ограничение перебора (опц.): 5 неудачных входов с одного email за 5 минут → сообщение «попробуйте позже» (in-memory dict).

---

## 7. i18n (контракт для обоих)

- Языки: `ru` (по умолчанию), `kk` (қазақша), `en`. Файлы `app/i18n/{ru,kk,en}.json`, **плоские ключи** через точку: `"landing.hero.title": "..."`.
- Выбор языка: `?lang=` → cookie `lang` → `user.preferred_lang` → `ru`.
- В шаблонах: `{{ t('landing.hero.title') }}`, с параметрами: `{{ t('search.summary.partial', n=2, total=10) }}` → в JSON `"Подобрали {n} из {total}"` (Python `str.format`).
- Нет ключа в выбранном языке → берём `ru` → если и там нет, показываем сам ключ (так пропуски видно на глаз).
- **Значения данных** (категории, форматы, города, языки) переводятся через ключи `data.category.<ru_value>`, `data.format.<ru_value>`, `data.city.<ru_value>`, `data.language.<ru_value>`. Внутри движка и API значения **всегда на русском, как в CSV**.
- Тексты объяснений собираются из атомов по шаблонам `explain.*` — поэтому тоже трёхъязычные. Цитаты из описаний остаются на языке оригинала (русский) и помечаются «по описанию».
- Главный разработчик добавляет новый ключ сразу в `ru.json` (+ пишет его в чат/коммит); Участник 2 дублирует в `kk.json` и `en.json`.

Официальные казахские термины берём из KZ-версии ТЗ (см. `01_REFERENCE.md`, раздел «Глоссарий»).

---

## 8. Контракт движка (`matcher/models.py`)

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

Status = Literal["found", "partial", "no_category_in_city", "none_match", "invalid_request"]
ReasonCode = Literal["busy", "format", "budget", "language", "duration"]

@dataclass(frozen=True)
class Contractor:
    id: str; name: str; categories: tuple[str, ...]; city: str
    price_from_kzt: int; event_formats: tuple[str, ...]; languages: tuple[str, ...]
    max_hours: Optional[int]; busy_dates: frozenset[str]; description: str
    synthetic: bool; city_imputed: bool; price_imputed: bool

@dataclass(frozen=True)
class SearchRequest:
    city: str; date: str            # "YYYY-MM-DD"
    event_type: str; category: str; budget_kzt: int
    duration_h: Optional[int] = None; language: Optional[str] = None
    wishes: Optional[str] = None    # свободный текст «пожелания», влияет на relevance и цитаты
    lang: str = "ru"                # язык интерфейса для текстов объяснений

@dataclass
class Atom:
    type: str                        # budget|format_focus|language|duration|quote|experience|venue_multi|flag|contrast|availability
    text: str
    unique: bool = False
    weight: float = 0.0

@dataclass
class Card:
    id: str; name: str; category: str; city: str; price_from_kzt: int
    badges: list[str]                # synthetic|price_imputed|city_imputed|price_equals_budget
    explanation: str                 # 1–2 предложения
    atoms: list[Atom]
    score: float
    score_breakdown: dict[str, float]

@dataclass
class Rejection:
    id: str; name: str; reasons: list[ReasonCode]; details: dict[str, str]

@dataclass
class SearchResponse:
    status: Status
    summary: str                     # одна строка для баннера
    cards: list[Card]                # ≤ 3
    more_count: int                  # сколько ещё подходят, но ниже в рейтинге
    rejected: list[Rejection]
    reason_counts: dict[str, int]    # {"busy": 4, "format": 3, "budget": 1}
    funnel: list[dict]               # [{"step":"category_city","n":10}, {"step":"free_on_date","n":6}, ...]
    hints: list[dict]                # [{"type":"date","text":"..."}]
    meta: dict                       # {"engine":"1.0","llm_used":false,"latency_ms":12}
```

Статусы:

- `found` — прошли ≥ 3: топ-3 + `more_count`.
- `partial` — прошли 1–2: карточки + причины отсева с именами.
- `no_category_in_city` — в городе 0 профилей этой категории → подсказка «есть в <город>: N».
- `none_match` — кандидаты есть, прошли 0 → разбивка причин + подсказки (дата/бюджет).
- `invalid_request` — дата вне окна 2026-09-23…2026-12-31, бюджет ≤ 0, неизвестные город/категория/формат/язык.

Детерминизм: никакого random; сортировка `(-score, price, id)`; score округляем до 4 знаков; JSON-ответ сериализуем с `sort_keys=True` в тестах.

---

## 9. Дизайн-система

Визуальный источник — [дизайнбук Tandau](TANDAU_DESIGNBOOK.md), реализация общего слоя описана в [фазе 1](PHASE_1_FOUNDATION_AND_LANDING.md). Прежняя бирюзово-золотая палитра и автоматическая тёмная тема заменены утверждённой системой.

| Назначение | Значение |
| --- | --- |
| Текст и основное действие | `#000000` |
| Основная поверхность | `#FFFFFF` |
| Вложенная поверхность | `#F5F5F5` |
| Вторичный текст | `#525252` |
| Акцент выбора и фокус | `#2B5FE3` |
| Панели | Радиус 0 px |
| Кнопки и поля | Радиус 4 px |
| Метки | Радиус 2 px |
| Всплывающие слои | Радиус 8 px |
| Шрифт | Локальный Geist с системным fallback |

Общие компоненты переносятся в основной слой приложения. Макетные CSS-файлы не подключаются все вместе глобально. Семантический цвет всегда сопровождается текстом и иконкой. Новые предметные 3D-ассеты ожидаются от владельца и не блокируют типографическую композицию.

---

## 10. Переменные окружения (`.env.example`)

```dotenv
# Всё необязательно — без .env приложение запускается с безопасными значениями по умолчанию
SECRET_KEY=
DATABASE_PATH=var/tandau.db
LLM_MODE=off                 # off | on
OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_BASE_URL=             # пусто = OpenAI; можно указать OpenAI-совместимый эндпоинт
```

---

## 11. Коммиты и ветки

- Работаем в `main`, мелкими коммитами. Stretch (LLM, кабинет) — в ветках `feat/llm`, `feat/account`, мёрж только когда `pytest` зелёный.
- Формат сообщений: `feat: …`, `fix: …`, `docs: …`, `test: …`, `chore: …`, `i18n: …` (Участник 2).
- Минимальный набор коммитов по часам — таблица в разделе 1. Лучше коммитить каждые 15–20 минут.
- Перед каждым push: `python -m pytest -q` (с фазы 4) и `git status` без `.env`/`var/`.

---

## 12. Definition of Done всего проекта (проверяем в 17:15–17:40)

- [ ] `git clone` в пустую папку → `python -m venv .venv` → `pip install -r requirements.txt` → `python run.py` → открывается `http://127.0.0.1:8000`
- [ ] Лендинг на трёх языках, переключатель работает, статистика берётся из данных (66 / 17 / 3)
- [ ] Регистрация, вход, выход работают; демо-аккаунт из README входит
- [ ] Подбор работает **без входа**
- [ ] 5 демо-сценариев из `01_REFERENCE.md` дают ожидаемые статусы и карточки
- [ ] Повтор запроса → идентичный JSON; две даты → разная выдача с причиной «занят»
- [ ] Объяснения без стоп-фраз, попарно различимы без имён, с числами и/или цитатой
- [ ] Ответ < 10 с (реально < 100 мс без LLM)
- [ ] `pytest -q` зелёный
- [ ] README: описание, архитектура, технологии, установка, запуск, зависимости, переменные окружения, сценарий проверки, данные, ограничения, использованные компоненты и AI-инструменты, демо-аккаунт
- [ ] В репозитории нет ключей (`git grep -nE "sk-|nvapi-"` пусто), `.env` и `var/` не закоммичены
- [ ] Коммит есть в каждом часовом окне (`git log --since="13:00" --date=format:%H:%M --format="%ad %an %s"`)
- [ ] На платформе нажато «Сдать решение», заполнены название и описание

---

## 13. Как работать с документами фаз

1. Открыть `docs/PHASE_N_*.md`, прочитать разделы «Цель», «Границы», «Критерии приёмки».
2. Для фазы 1 следовать пакетам P1-A…P1-G новой спецификации. Код из других документов адаптировать к актуальной основе; не выполнять полные замены файлов без сверки.
3. Проверить по «Критериям приёмки», прогнать тесты фазы, закоммитить с сообщением из раздела «Коммиты».
4. Пересматривать объём по фактической готовности. Старые тайм-боксы не отменяют актуальные критерии приёмки.

Файлы:

- `00_MASTER_PLAN.md` — этот документ
- `01_REFERENCE.md` — ТЗ, правила хакатона, факты о данных, демо-сценарии, глоссарий RU/KZ/EN
- `PHASE_1_FOUNDATION_AND_LANDING.md`
- `PHASE_2_REGISTRATION.md`
- `PHASE_3_LOGIN_AND_SESSIONS.md`
- `PHASE_4_MATCHING_ENGINE.md`
- `PHASE_5_EXPLANATIONS_AND_HONESTY.md`
- `PHASE_6_ACCOUNT_AND_PROFILES.md`
- `PHASE_7_QUALITY_README_SUBMISSION.md`
- `ISSUE_i18n_and_minor_tasks.md` — задача для Участника 2
