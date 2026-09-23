# Фаза 1 — Фундамент и лендинг

| | |
| --- | --- |
| Время | **14:10–14:50** (40 минут) |
| Владелец | Главный разработчик |
| Параллельно | Участник 2 — `app/i18n/*.json` (ключи из раздела 11), логотип и favicon |
| Зависит от | `00_MASTER_PLAN.md` (стек, структура, контракты), `01_REFERENCE.md` (данные) |
| Коммиты | 14:30 `feat: skeleton`, 14:50 `feat: landing` — закрывают окно 14:00–15:00 |
| На выходе | `python run.py` поднимает сайт; лендинг на трёх языках со статистикой из данных; `/healthz`, `/api/meta`; каталог 66 профилей загружен и покрыт тестами |

---

## 1. Цель фазы и где здесь баллы

Фаза закладывает всё, на чём стоят фазы 2–7, и даёт первое, что увидит жюри и эксперт.

| Критерий | Что даёт фаза 1 |
| --- | --- |
| README и воспроизводимость (25) | Запуск одной командой без Node, без БД-сервера, без обязательного `.env`. Эксперт открывает `http://127.0.0.1:8000` сразу |
| Техническая реализация (25) | Чистое разделение: `matcher/` — домен без веба, `app/` — веб-слой. Swagger `/docs` из коробки |
| Ценность (15) | Лендинг за 10 секунд объясняет, чем продукт полезен заказчику и агрегатору |
| Соответствие ТЗ (25) | Загрузчик данных с правильным парсингом — фундамент всех 6 требований (списки через `\|`, `True/False`, пустой `max_hours`) |

**Жёсткое ограничение:** ТЗ прямо говорит, что красивый UI не входит в оценку. Лендинг делаем аккуратным, но **не больше 20 минут** на вёрстку. Всё остальное время — на каркас и данные.

---

## 2. Границы

**Входит:**

- Скелет репозитория по структуре из мастер-плана (раздел 3).
- `run.py`, `requirements.txt`, `.env.example`, `.gitignore`, заглушка `README.md` с обязательными разделами.
- `app/config.py` — настройки из env + автогенерация `SECRET_KEY` в `var/secret_key`.
- `app/main.py` — фабрика приложения, сессии, статика, роутеры.
- `app/i18n.py` + `app/web.py` (хелпер `render()`), переключатель языка, три файла словарей (минимум ключи этой фазы).
- `matcher/models.py` (класс `Contractor`), `matcher/data.py` (загрузка и индексы каталога).
- Базовый шаблон, шапка, подвал, лендинг.
- `app/static/css/app.css` — дизайн-система (токены + компоненты), `app/static/js/app.js` — мобильное меню.
- API: `GET /healthz`, `GET /api/meta`, `GET /lang/{code}`.
- Тесты `tests/test_data.py`, `tests/test_pages.py`.

**Не входит (будет позже):**

- БД, пользователи, формы входа/регистрации — фазы 2–3 (в шапке уже есть ссылки на них, страницы пока отдают заглушку или 404 — это нормально до 15:10).
- Движок подбора и страница `/app` — фаза 4 (кнопка «Подобрать» ведёт на `/app`; до фазы 4 там заглушка «скоро»).
- Анимации, иллюстрации, картинки с интернета, CDN-шрифты — не делаем вообще.

---

## 3. Пользовательские истории

**US-1.1 Эксперт запускает проект**
Дано: чистый клон, Python 3.10+. Когда: `pip install -r requirements.txt && python run.py`. Тогда: в консоли `Uvicorn running on http://127.0.0.1:8000`, страница открывается, `.env` не нужен.

**US-1.2 Заказчик понимает продукт**
Дано: открыт `/`. Тогда: за один экран видны заголовок-обещание, подзаголовок «как», две кнопки: «Подобрать без регистрации» → `/app`, «Создать аккаунт» → `/register`.

**US-1.3 Заказчик видит, что сервис честный**
Дано: прокрутил лендинг. Тогда: видит блок с тремя исходами (подобрали / категории нет в городе / кандидаты есть, но никто не проходит) с реальными примерами из каталога и пример карточки с объяснением.

**US-1.4 Пользователь переключает язык**
Когда: нажимает «Қаз» в шапке. Тогда: страница перерисовывается на казахском, выбор сохраняется в cookie `lang` на год; на других страницах язык тот же.

**US-1.5 Интегратор проверяет API**
Когда: открывает `/docs`. Тогда: видит `GET /healthz` и `GET /api/meta`; `/api/meta` возвращает 3 города, 17 категорий с разбивкой по городам, 6 форматов, 3 языка, окно дат.

**US-1.6 Цифры на лендинге честные**
Тогда: «66 профилей · 17 категорий · 3 города · 100 дней календаря · 13 синтетических помечены» считаются из CSV при старте, а не захардкожены.

---

## 4. UX: экраны и состояния

### 4.1 Шапка (на всех страницах)

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ [◆ Tandau]      Подбор     Как это работает        Рус | Қаз | Eng   [Войти] [Регистрация] │
└──────────────────────────────────────────────────────────────────────────┘
Мобильная (< 720px):
┌────────────────────────────┐
│ [◆ Tandau]            [☰] │   ☰ раскрывает вертикальное меню
└────────────────────────────┘
```

Для вошедшего пользователя (с фазы 3) вместо «Войти/Регистрация»: «Кабинет», «Выйти».

### 4.2 Лендинг (сверху вниз)

```text
┌─ HERO ───────────────────────────────────────────────────────────────────┐
│  Три подрядчика — и честное объяснение, почему именно они                 │
│  Укажите город, дату, тип мероприятия и бюджет. Мы уберём занятых и       │
│  неподходящих, а по каждому выбранному объясним, чем он подходит вам.     │
│  [ Подобрать без регистрации ]   [ Создать аккаунт ]                      │
│  66 профилей · 17 категорий · 3 города · 100 дней календаря               │
└──────────────────────────────────────────────────────────────────────────┘
┌─ КАК ЭТО РАБОТАЕТ ───────────────────────────────────────────────────────┐
│ ① Параметры заказа     ② Честные фильтры        ③ До трёх карточек        │
│ город, дата, тип...     убираем занятых...        с объяснением-фактами   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ ТАК ВЫГЛЯДИТ ОБЪЯСНЕНИЕ ────────────────────────────────────────────────┐
│ Запрос: Алматы · 17 октября · свадьба · ведущий · до 1 000 000 ₸ · каз. · 8 ч│
│ ┌ Эмилия ─────────────┐ ┌ Кики ───────────────┐ ┌ Хаул ───────────────┐   │
│ │ Ведущий · Алматы     │ │ Ведущий · Алматы     │ │ Ведущий · Алматы     │   │
│ │ от 900 000 ₸ [цена*] │ │ от 900 000 ₸         │ │ от 1 000 000 ₸       │   │
│ │ Свадьбы — узкий      │ │ Единственный из трёх │ │ Актёр и телеведущий  │   │
│ │ профиль…             │ │ с английским…        │ │ по описанию…         │   │
│ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ ЕСЛИ ПОДОБРАТЬ НЕЛЬЗЯ — СКАЖЕМ ПОЧЕМУ ──────────────────────────────────┐
│ [✓ зелёный]  Подобрали 3 из 10 ведущих Алматы                             │
│ [i синий]    В Астане декораторов нет — в Алматы их 3                     │
│ [! красный]  26 декабря 9 из 10 ведущих заняты, свободный не ведёт тои     │
└──────────────────────────────────────────────────────────────────────────┘
┌─ КАТАЛОГ В ЦИФРАХ ───────────────────────────────────────────────────────┐
│ 66 профилей │ 17 категорий │ 3 города │ 100 дней │ 13 синтетических       │
│ Категории: [Ведущий 15] [Фотограф 12] [Банкетный зал 8] [Ресторан 7] ...   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ ВОПРОСЫ ────────────────────────────────────────────────────────────────┐
│ ▸ Нужна ли регистрация?  ▸ Откуда данные?  ▸ Почему именно эти три?       │
│ ▸ Одинаковый запрос — одинаковый ответ?                                   │
└──────────────────────────────────────────────────────────────────────────┘
┌─ ПОДВАЛ ─────────────────────────────────────────────────────────────────┐
│ Tandau — прототип для HackAlem AI · API и документация (/docs)             │
└──────────────────────────────────────────────────────────────────────────┘
```

Пример карточек на лендинге — **статичный** (тексты из `01_REFERENCE.md`, сценарий S2 на 17.10). В фазе 5 можно заменить на живой вызов движка, но это не обязательно.

### 4.3 Состояния и доступность

- Все кнопки — настоящие `<a>`/`<button>`, фокус виден (`:focus-visible` с обводкой `--c-primary`).
- Контраст текста ≥ 4.5:1 (токены из мастер-плана это дают).
- Баннеры исходов: иконка + текст + цвет (цвет не единственный носитель смысла).
- `<html lang="ru|kk|en">` меняется вместе с языком.
- FAQ на `<details>/<summary>` — без JS.
- Ширина контента — `max-width: 1120px`, поля 16px на мобильных; сетки карточек схлопываются в одну колонку на < 720px.

---

## 5. Маршруты и API этой фазы

| Метод | Путь | Ответ | Код |
| --- | --- | --- | --- |
| GET | `/` | HTML лендинга | 200 |
| GET | `/lang/{code}` | Ставит cookie `lang`, редирект на `Referer` или `/` | 303 (неизвестный код → 303 без cookie) |
| GET | `/healthz` | `{"status":"ok","profiles":66}` | 200 |
| GET | `/api/meta` | см. ниже | 200 |
| GET | `/app` | Заглушка «Подбор появится в фазе 4» (временно) | 200 |

Пример `/api/meta`:

```bash
curl -s http://127.0.0.1:8000/api/meta | python -m json.tool
```

```json
{
  "cities": ["Алматы", "Астана", "Зарубежье"],
  "categories": [
    {"name": "Ведущий", "total": 15, "by_city": {"Алматы": 10, "Астана": 5}},
    {"name": "Фотограф", "total": 12, "by_city": {"Алматы": 8, "Астана": 3, "Зарубежье": 1}},
    {"name": "Банкетный зал", "total": 8, "by_city": {"Алматы": 7, "Астана": 1}}
  ],
  "event_formats": ["свадьба", "той", "корпоратив", "конференция", "юбилей", "день рождения"],
  "languages": ["русский", "казахский", "английский"],
  "window": {"start": "2026-09-23", "end": "2026-12-31", "days": 100},
  "stats": {"profiles": 66, "categories": 17, "cities": 3, "synthetic": 13, "price_imputed": 18, "city_imputed": 8}
}
```

(в ответе все 17 категорий, отсортированы по `total` убыв., затем по имени).

---

## 6. Модели данных этой фазы

Только доменная модель подрядчика и каталог (БД появится в фазе 2).

```python
# matcher/models.py  — фаза 1 создаёт Contractor; остальные классы добавит фаза 4
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Contractor:
    id: str
    name: str
    categories: tuple[str, ...]
    city: str
    price_from_kzt: int
    event_formats: tuple[str, ...]
    languages: tuple[str, ...]
    max_hours: Optional[int]
    busy_dates: frozenset[str]
    description: str
    synthetic: bool
    city_imputed: bool
    price_imputed: bool

    def is_free(self, date_iso: str) -> bool:
        return date_iso not in self.busy_dates

    def has_category(self, category: str) -> bool:
        return category in self.categories   # по элементу! «Ведущий» ≠ «Ведущий церемонии»
```

---

## 7. Файлы фазы

```text
run.py                                   NEW
requirements.txt                         NEW (из мастер-плана, раздел 2)
requirements-llm.txt                     NEW
.env.example                             NEW (из мастер-плана, раздел 10)
.gitignore                               NEW
README.md                                NEW (скелет, раздел 10.9 ниже)
data/hackathon-dataset-anonymized.csv    NEW (уже скачан: openai/data/)
matcher/__init__.py                      NEW (пустой)
matcher/models.py                        NEW
matcher/data.py                          NEW
app/__init__.py                          NEW (пустой)
app/config.py                            NEW
app/i18n.py                              NEW
app/web.py                               NEW  ← хелпер render(); используется всеми страницами фаз 2–7
app/main.py                              NEW
app/routes/__init__.py                   NEW (пустой)
app/routes/pages.py                      NEW
app/routes/api.py                        NEW
app/i18n/ru.json, kk.json, en.json       NEW (ru — главный разработчик; kk/en — Участник 2)
app/templates/base.html                  NEW
app/templates/partials/header.html       NEW
app/templates/partials/footer.html       NEW
app/templates/partials/lang_switch.html  NEW
app/templates/landing.html               NEW
app/templates/app/placeholder.html       NEW (временная заглушка /app до фазы 4)
app/static/css/app.css                   NEW
app/static/js/app.js                     NEW
app/static/img/logo.svg, favicon.svg     NEW (Участник 2; до этого — текстовый логотип)
tests/__init__.py                        NEW (пустой)
tests/conftest.py                        NEW
tests/test_data.py                       NEW
tests/test_pages.py                      NEW
```

`app/web.py` — единственное дополнение к структуре мастер-плана: один хелпер рендера на всё приложение.

---

## 8. Пошаговый план (по минутам)

| Время | Шаг | Готово, если |
| --- | --- | --- |
| 14:10–14:14 | Клонировать командный репозиторий, скопировать `data/` и `docs/` из папки `openai`, создать venv | `git status` видит файлы |
| 14:14–14:18 | `requirements.txt`, `.gitignore`, `.env.example`, `run.py`, пустые `__init__.py` | `pip install -r requirements.txt` ставится |
| 14:18–14:24 | `matcher/models.py`, `matcher/data.py`, `tests/test_data.py` | `pytest tests/test_data.py -q` зелёный |
| 14:24–14:30 | `app/config.py`, `app/i18n.py`, `app/web.py`, `app/main.py`, `routes/api.py` (`/healthz`, `/api/meta`) | `python run.py`, `/healthz` → 66 |
| **14:30** | **Коммит + push `feat: skeleton, data loader, meta api`** | виден на GitHub |
| 14:30–14:35 | `base.html`, `header.html`, `footer.html`, `lang_switch.html`, `app.css` (токены + базовые компоненты) | шапка и подвал рисуются |
| 14:35–14:45 | `landing.html` по разделу 4.2 + `ru.json` ключи раздела 11 | лендинг читается на русском |
| 14:45–14:48 | `/lang/{code}`, `tests/test_pages.py`, заглушка `/app` | `pytest -q` зелёный |
| **14:48–14:50** | **Коммит + push `feat: landing page with live catalog stats`** | виден на GitHub |

Если к 14:40 лендинг не готов — выкинуть блок «Так выглядит объяснение» и FAQ, оставить hero + как это работает + честность + цифры.

---

## 9. Как запускать (вставить в README сразу)

```bash
git clone <URL командного репозитория> tandau && cd tandau
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
# открыть http://127.0.0.1:8000
```

---

## 10. Код

Код ниже рабочий и минимальный. Codex может его дописывать, но **имена файлов, функций и маршрутов не менять** — на них опираются фазы 2–7.

### 10.1 `run.py`

```python
import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
```

### 10.2 `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
var/
cache/
.DS_Store
```

### 10.3 `app/config.py`

```python
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Минимальный загрузчик .env без внешних зависимостей. Переменные окружения важнее файла."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.split(" #", 1)[0].strip())


_load_dotenv(BASE_DIR / ".env")


def _secret_key(var_dir: Path) -> str:
    env_value = os.getenv("SECRET_KEY", "").strip()
    if env_value:
        return env_value
    var_dir.mkdir(parents=True, exist_ok=True)
    key_file = var_dir / "secret_key"
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()
    key = secrets.token_urlsafe(48)
    key_file.write_text(key, encoding="utf-8")
    return key


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    data_path: Path
    database_path: Path
    secret_key: str
    llm_mode: str
    openai_api_key: str
    openai_model: str
    openai_base_url: str


def get_settings() -> Settings:
    var_dir = BASE_DIR / "var"
    db_value = os.getenv("DATABASE_PATH", "").strip() or "var/tandau.db"
    db_path = Path(db_value)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    return Settings(
        base_dir=BASE_DIR,
        data_path=BASE_DIR / "data" / "hackathon-dataset-anonymized.csv",
        database_path=db_path,
        secret_key=_secret_key(var_dir),
        llm_mode=(os.getenv("LLM_MODE", "off").strip().lower() or "off"),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
    )


settings = get_settings()
```

### 10.4 `matcher/data.py`

```python
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import Contractor

WINDOW_START = "2026-09-23"
WINDOW_END = "2026-12-31"
WINDOW_DAYS = 100
EVENT_FORMATS = ("свадьба", "той", "корпоратив", "конференция", "юбилей", "день рождения")
LANGUAGES = ("русский", "казахский", "английский")
CITIES = ("Алматы", "Астана", "Зарубежье")


def _split(value: Optional[str]) -> tuple[str, ...]:
    return tuple(part.strip() for part in (value or "").split("|") if part.strip())


def _bool(value: Optional[str]) -> bool:
    # В файле True/False; в Google-превью TRUE/FALSE — поддерживаем оба
    return (value or "").strip().lower() == "true"


def _int_or_none(value: Optional[str]) -> Optional[int]:
    value = (value or "").strip()
    return int(value) if value else None


def parse_row(row: dict) -> Contractor:
    return Contractor(
        id=row["id"].strip(),
        name=row["anon_name"].strip(),
        categories=_split(row["categories"]),
        city=row["city"].strip(),
        price_from_kzt=int(row["price_from_kzt"]),
        event_formats=_split(row["event_formats"]),
        languages=_split(row["languages"]),
        max_hours=_int_or_none(row["max_hours"]),
        busy_dates=frozenset(_split(row["busy_dates"])),
        description=(row.get("description") or "").strip(),
        synthetic=_bool(row["synthetic"]),
        city_imputed=_bool(row["city_imputed"]),
        price_imputed=_bool(row["price_imputed"]),
    )


@dataclass(frozen=True)
class Catalog:
    contractors: tuple[Contractor, ...]
    by_id: dict[str, Contractor]
    category_city_counts: dict[str, dict[str, int]]
    categories: tuple[str, ...]     # по убыванию количества, затем по алфавиту

    def in_category_city(self, category: str, city: str) -> list[Contractor]:
        return [c for c in self.contractors if c.has_category(category) and c.city == city]

    def stats(self) -> dict:
        return {
            "profiles": len(self.contractors),
            "categories": len(self.categories),
            "cities": len({c.city for c in self.contractors}),
            "days": WINDOW_DAYS,
            "synthetic": sum(c.synthetic for c in self.contractors),
            "price_imputed": sum(c.price_imputed for c in self.contractors),
            "city_imputed": sum(c.city_imputed for c in self.contractors),
        }

    def category_rows(self) -> list[dict]:
        rows = []
        for name in self.categories:
            by_city = self.category_city_counts[name]
            rows.append({"name": name, "total": sum(by_city.values()), "by_city": dict(by_city)})
        return rows

    def meta(self) -> dict:
        return {
            "cities": list(CITIES),
            "categories": self.category_rows(),
            "event_formats": list(EVENT_FORMATS),
            "languages": list(LANGUAGES),
            "window": {"start": WINDOW_START, "end": WINDOW_END, "days": WINDOW_DAYS},
            "stats": self.stats(),
        }


def load_catalog(path: Path) -> Catalog:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        contractors = tuple(parse_row(row) for row in csv.DictReader(fh))
    counts: dict[str, Counter] = defaultdict(Counter)
    for c in contractors:
        for cat in c.categories:
            counts[cat][c.city] += 1
    categories = tuple(sorted(counts, key=lambda k: (-sum(counts[k].values()), k)))
    return Catalog(
        contractors=contractors,
        by_id={c.id: c for c in contractors},
        category_city_counts={k: dict(v) for k, v in counts.items()},
        categories=categories,
    )
```

### 10.5 `app/i18n.py`

```python
from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request

SUPPORTED = ("ru", "kk", "en")
DEFAULT_LANG = "ru"
HTML_LANG = {"ru": "ru", "kk": "kk", "en": "en"}
_LOCALES: dict[str, dict[str, str]] = {}


def load_locales(directory: Path) -> None:
    for code in SUPPORTED:
        path = directory / f"{code}.json"
        _LOCALES[code] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def translate(lang: str, key: str, **kwargs) -> str:
    text = _LOCALES.get(lang, {}).get(key) or _LOCALES.get(DEFAULT_LANG, {}).get(key) or key
    if not kwargs:
        return text
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return text


def data_label(lang: str, kind: str, value: str) -> str:
    """Перевод значения из данных: kind = category | format | city | language."""
    return translate(lang, f"data.{kind}.{value}") if value else value


def get_lang(request: Request) -> str:
    query = request.query_params.get("lang")
    if query in SUPPORTED:
        return query
    cookie = request.cookies.get("lang")
    if cookie in SUPPORTED:
        return cookie
    user = getattr(request.state, "user", None)          # появится в фазе 3
    if user and user.get("preferred_lang") in SUPPORTED:
        return user["preferred_lang"]
    return DEFAULT_LANG
```

Правило для `data_label`: если перевода нет, `translate` вернёт сам ключ `data.category.Ведущий`. Чтобы на экране не появлялся ключ, в `ru.json` **обязательно** есть все значения данных (раздел 11.3), а `kk/en` при пропуске откатываются на `ru`.

### 10.6 `app/web.py`

```python
from __future__ import annotations

import secrets

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .config import settings
from .i18n import HTML_LANG, SUPPORTED, data_label, get_lang, translate

templates = Jinja2Templates(directory=str(settings.base_dir / "app" / "templates"))


def format_kzt(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₸"


templates.env.filters["kzt"] = format_kzt


def ensure_csrf(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def render(request: Request, name: str, status_code: int = 200, **context):
    lang = get_lang(request)
    base = {
        "lang": lang,
        "html_lang": HTML_LANG[lang],
        "t": lambda key, **kw: translate(lang, key, **kw),
        "label": lambda kind, value: data_label(lang, kind, value),
        "user": getattr(request.state, "user", None),
        "csrf": ensure_csrf(request),
        "path": request.url.path,
    }
    base.update(context)
    response = templates.TemplateResponse(request, name, base, status_code=status_code)
    if request.query_params.get("lang") in SUPPORTED:
        response.set_cookie("lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response
```

### 10.7 `app/main.py`

```python
from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from matcher.data import load_catalog

from .config import settings
from .i18n import load_locales
from .routes import api, pages


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tandau API",
        version="1.0.0",
        description="Подбор event-подрядчиков с объяснениями: до 3 карточек и честное «почему не больше».",
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="tandau_session",
        max_age=7 * 24 * 3600,
        same_site="lax",
        https_only=False,
    )
    app.mount("/static", StaticFiles(directory=str(settings.base_dir / "app" / "static")), name="static")
    load_locales(settings.base_dir / "app" / "i18n")
    app.state.catalog = load_catalog(settings.data_path)
    app.include_router(pages.router)
    app.include_router(api.router)
    # фаза 2: init_db() + seed_demo_user() + app.include_router(auth.router)
    # фаза 3: middleware, кладущий пользователя в request.state.user
    return app


app = create_app()
```

### 10.8 `app/routes/pages.py` и `app/routes/api.py`

```python
# app/routes/pages.py
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..i18n import SUPPORTED
from ..web import render

router = APIRouter()

EXAMPLE_CARDS = [  # сценарий S2 на 17.10 из 01_REFERENCE.md; тексты — ключи i18n
    {"name": "Эмилия", "category": "Ведущий", "city": "Алматы", "price": 900_000,
     "badges": ["price_imputed"], "text_key": "landing.example.card1"},
    {"name": "Кики", "category": "Ведущий", "city": "Алматы", "price": 900_000,
     "badges": [], "text_key": "landing.example.card2"},
    {"name": "Хаул", "category": "Ведущий", "city": "Алматы", "price": 1_000_000,
     "badges": ["price_equals_budget"], "text_key": "landing.example.card3"},
]


@router.get("/", response_class=HTMLResponse)
def landing(request: Request):
    catalog = request.app.state.catalog
    return render(
        request,
        "landing.html",
        stats=catalog.stats(),
        categories=catalog.category_rows(),
        example_cards=EXAMPLE_CARDS,
    )


@router.get("/lang/{code}")
def switch_lang(code: str, request: Request):
    target = request.headers.get("referer") or "/"
    response = RedirectResponse(target, status_code=303)
    if code in SUPPORTED:
        response.set_cookie("lang", code, max_age=365 * 24 * 3600, samesite="lax")
    return response


@router.get("/app", response_class=HTMLResponse)
def app_placeholder(request: Request):  # заменяется в фазе 4
    return render(request, "app/placeholder.html")
```

```python
# app/routes/api.py
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/healthz", tags=["service"])
def healthz(request: Request) -> dict:
    return {"status": "ok", "profiles": len(request.app.state.catalog.contractors)}


@router.get("/api/meta", tags=["catalog"])
def meta(request: Request) -> dict:
    """Справочники для формы подбора: города, категории с количеством по городам, форматы, языки, окно дат."""
    return request.app.state.catalog.meta()
```

`/lang/{code}` безопасен от открытого редиректа только если `Referer` с того же хоста. Минимальная защита: если `Referer` не начинается с `str(request.base_url)`, редиректить на `/`.

### 10.9 Скелет `README.md` (дописывается в фазе 7)

```markdown
# Tandau — подбор event-подрядчиков с объяснениями

> Прототип для HackAlem AI, трек «Креативные индустрии», кейс Firebird «Умный подбор подрядчиков».

## Что делает проект
## Что реализовано
## Как это работает
## Технологии
## Архитектура
## Установка и запуск
## Демо-доступ
## Как проверить решение
## Данные и внешние сервисы
## Переменные окружения
## Тесты
## Ограничения
## Использованные компоненты и AI-инструменты
## Языки интерфейса
```

### 10.10 `app/templates/base.html`

```html
<!doctype html>
<html lang="{{ html_lang }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Tandau{% endblock %}</title>
  <meta name="description" content="{{ t('meta.description') }}">
  <link rel="icon" href="/static/img/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
  <a class="skip-link" href="#main">{{ t('common.skip_to_content') }}</a>
  {% include "partials/header.html" %}
  <main id="main" class="page">
    {% block content %}{% endblock %}
  </main>
  {% include "partials/footer.html" %}
  <script src="/static/js/app.js" defer></script>
</body>
</html>
```

### 10.11 `app/templates/partials/header.html` и `lang_switch.html`

```html
<header class="site-header">
  <div class="container site-header__inner">
    <a class="logo" href="/" aria-label="Tandau">
      <span class="logo__mark" aria-hidden="true">◆</span><span class="logo__text">Tandau</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="visually-hidden">{{ t('nav.menu') }}</span>☰
    </button>
    <nav id="site-nav" class="site-nav" aria-label="{{ t('nav.menu') }}">
      <a href="/app" class="site-nav__link {% if path.startswith('/app') %}is-active{% endif %}">{{ t('nav.search') }}</a>
      <a href="/#how" class="site-nav__link">{{ t('nav.how') }}</a>
      {% include "partials/lang_switch.html" %}
      {% if user %}
        <a href="/account/history" class="btn btn--ghost">{{ t('nav.account') }}</a>
        <form method="post" action="/logout" class="inline-form">
          <input type="hidden" name="csrf" value="{{ csrf }}">
          <button class="btn btn--ghost" type="submit">{{ t('nav.logout') }}</button>
        </form>
      {% else %}
        <a href="/login" class="btn btn--ghost">{{ t('nav.login') }}</a>
        <a href="/register" class="btn btn--primary">{{ t('nav.register') }}</a>
      {% endif %}
    </nav>
  </div>
</header>
```

```html
<div class="lang-switch" role="group" aria-label="{{ t('nav.language') }}">
  {% for code, label in [('ru', 'Рус'), ('kk', 'Қаз'), ('en', 'Eng')] %}
    <a href="/lang/{{ code }}" class="lang-switch__item {% if lang == code %}is-active{% endif %}"
       {% if lang == code %}aria-current="true"{% endif %} hreflang="{{ code }}">{{ label }}</a>
  {% endfor %}
</div>
```

### 10.12 `app/templates/partials/footer.html`

```html
<footer class="site-footer">
  <div class="container site-footer__inner">
    <p>{{ t('footer.text') }}</p>
    <p><a href="/docs">{{ t('footer.api') }}</a> · <a href="/healthz">healthz</a></p>
  </div>
</footer>
```

### 10.13 `app/templates/landing.html`

```html
{% extends "base.html" %}
{% block title %}Tandau — {{ t('landing.hero.title_short') }}{% endblock %}
{% block content %}

<section class="hero">
  <div class="container">
    <h1 class="hero__title">{{ t('landing.hero.title') }}</h1>
    <p class="hero__subtitle">{{ t('landing.hero.subtitle') }}</p>
    <div class="hero__actions">
      <a class="btn btn--primary btn--lg" href="/app">{{ t('landing.hero.cta_primary') }}</a>
      <a class="btn btn--ghost btn--lg" href="/register">{{ t('landing.hero.cta_secondary') }}</a>
    </div>
    <p class="hero__stats">
      {{ t('landing.hero.stats', profiles=stats.profiles, categories=stats.categories, cities=stats.cities, days=stats.days) }}
    </p>
  </div>
</section>

<section id="how" class="section">
  <div class="container">
    <h2 class="section__title">{{ t('landing.how.title') }}</h2>
    <ol class="steps">
      {% for i in [1, 2, 3] %}
      <li class="step card">
        <span class="step__num" aria-hidden="true">{{ i }}</span>
        <h3 class="step__title">{{ t('landing.how.step' ~ i ~ '.title') }}</h3>
        <p class="step__text">{{ t('landing.how.step' ~ i ~ '.text') }}</p>
      </li>
      {% endfor %}
    </ol>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <h2 class="section__title">{{ t('landing.example.title') }}</h2>
    <p class="muted">{{ t('landing.example.query') }}</p>
    <div class="cards-grid">
      {% for c in example_cards %}
      <article class="card result-card">
        <header class="result-card__head">
          <h3 class="result-card__name">{{ c.name }}</h3>
          <p class="result-card__meta">{{ label('category', c.category) }} · {{ label('city', c.city) }}</p>
          <p class="result-card__price">{{ t('card.price_from', price=(c.price | kzt)) }}</p>
          {% for b in c.badges %}<span class="badge badge--{{ b }}">{{ t('badge.' ~ b) }}</span>{% endfor %}
        </header>
        <p class="result-card__text">{{ t(c.text_key) }}</p>
      </article>
      {% endfor %}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section__title">{{ t('landing.honesty.title') }}</h2>
    <ul class="outcomes">
      <li class="banner banner--found"><span class="banner__icon" aria-hidden="true">✓</span>{{ t('landing.honesty.found') }}</li>
      <li class="banner banner--nocat"><span class="banner__icon" aria-hidden="true">i</span>{{ t('landing.honesty.nocat') }}</li>
      <li class="banner banner--none"><span class="banner__icon" aria-hidden="true">!</span>{{ t('landing.honesty.none') }}</li>
    </ul>
  </div>
</section>

<section class="section section--alt">
  <div class="container">
    <h2 class="section__title">{{ t('landing.stats.title') }}</h2>
    <dl class="stats">
      <div class="stat"><dt>{{ t('landing.stats.profiles') }}</dt><dd>{{ stats.profiles }}</dd></div>
      <div class="stat"><dt>{{ t('landing.stats.categories') }}</dt><dd>{{ stats.categories }}</dd></div>
      <div class="stat"><dt>{{ t('landing.stats.cities') }}</dt><dd>{{ stats.cities }}</dd></div>
      <div class="stat"><dt>{{ t('landing.stats.days') }}</dt><dd>{{ stats.days }}</dd></div>
      <div class="stat"><dt>{{ t('landing.stats.synthetic') }}</dt><dd>{{ stats.synthetic }}</dd></div>
    </dl>
    <h3 class="subsection__title">{{ t('landing.categories.title') }}</h3>
    <ul class="chips">
      {% for cat in categories %}
      <li class="chip" title="{% for city, n in cat.by_city.items() %}{{ label('city', city) }}: {{ n }} {% endfor %}">
        {{ label('category', cat.name) }} <span class="chip__count">{{ cat.total }}</span>
      </li>
      {% endfor %}
    </ul>
  </div>
</section>

<section class="section">
  <div class="container faq">
    <h2 class="section__title">{{ t('landing.faq.title') }}</h2>
    {% for i in [1, 2, 3, 4] %}
    <details class="faq__item">
      <summary>{{ t('landing.faq.q' ~ i) }}</summary>
      <p>{{ t('landing.faq.a' ~ i) }}</p>
    </details>
    {% endfor %}
    <p class="faq__cta"><a class="btn btn--primary" href="/app">{{ t('landing.hero.cta_primary') }}</a></p>
  </div>
</section>

{% endblock %}
```

### 10.14 `app/templates/app/placeholder.html` (временная, до фазы 4)

```html
{% extends "base.html" %}
{% block content %}
<section class="section"><div class="container">
  <h1>{{ t('app.placeholder.title') }}</h1>
  <p class="muted">{{ t('app.placeholder.text') }}</p>
</div></section>
{% endblock %}
```

### 10.15 `app/static/css/app.css`

```css
/* ============ Токены (из мастер-плана, раздел 9) ============ */
:root {
  --c-bg: #F7F8FA; --c-surface: #FFFFFF; --c-text: #10151C; --c-muted: #5B6573;
  --c-border: #E3E7ED; --c-primary: #0096B7; --c-primary-ink: #FFFFFF; --c-primary-hover: #007F9B;
  --c-accent: #E8B100;
  --c-ok: #1B8A4B; --c-ok-bg: #E8F5EE; --c-warn: #B76E00; --c-warn-bg: #FFF4E0;
  --c-bad: #C62828; --c-bad-bg: #FDECEC; --c-info: #2F6FDB; --c-info-bg: #EAF1FD;
  --c-neutral-bg: #EEF1F4;
  --radius: 14px; --radius-sm: 10px;
  --shadow: 0 1px 2px rgba(16,21,28,.06), 0 8px 24px rgba(16,21,28,.06);
  --font: -apple-system, "Segoe UI", Roboto, "Noto Sans", "Helvetica Neue", Arial, sans-serif;
  --s1: 4px; --s2: 8px; --s3: 12px; --s4: 16px; --s5: 24px; --s6: 32px; --s7: 48px; --s8: 64px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --c-bg: #0E1216; --c-surface: #161B22; --c-text: #E8EDF2; --c-muted: #9AA6B2; --c-border: #262D36;
    --c-primary: #1FB6D6; --c-primary-hover: #49C7E2; --c-primary-ink: #04161B;
    --c-ok-bg: #12301F; --c-warn-bg: #33250A; --c-bad-bg: #3A1414; --c-info-bg: #122744; --c-neutral-bg: #1E252E;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.35);
  }
}

/* ============ База ============ */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; font: 16px/1.55 var(--font); color: var(--c-text); background: var(--c-bg); }
h1, h2, h3 { line-height: 1.2; margin: 0 0 var(--s3); }
p { margin: 0 0 var(--s3); }
a { color: var(--c-primary); }
a:hover { color: var(--c-primary-hover); }
:focus-visible { outline: 3px solid var(--c-primary); outline-offset: 2px; border-radius: 6px; }
.container { max-width: 1120px; margin: 0 auto; padding: 0 var(--s4); }
.page { min-height: 70vh; }
.muted { color: var(--c-muted); }
.visually-hidden { position: absolute !important; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.skip-link { position: absolute; left: -9999px; top: 0; background: var(--c-surface); padding: var(--s2) var(--s3); }
.skip-link:focus { left: var(--s3); z-index: 10; }
.inline-form { display: inline; margin: 0; }

/* ============ Кнопки ============ */
.btn { display: inline-flex; align-items: center; gap: var(--s2); padding: 10px 16px; border-radius: var(--radius-sm);
  border: 1px solid transparent; font: 600 15px/1 var(--font); text-decoration: none; cursor: pointer; background: none; color: var(--c-text); }
.btn--primary { background: var(--c-primary); color: var(--c-primary-ink); }
.btn--primary:hover { background: var(--c-primary-hover); color: var(--c-primary-ink); }
.btn--ghost { border-color: var(--c-border); background: var(--c-surface); }
.btn--ghost:hover { border-color: var(--c-primary); color: var(--c-primary); }
.btn--lg { padding: 14px 20px; font-size: 16px; }
.btn[disabled] { opacity: .5; cursor: not-allowed; }

/* ============ Шапка и подвал ============ */
.site-header { background: var(--c-surface); border-bottom: 1px solid var(--c-border); position: sticky; top: 0; z-index: 5; }
.site-header__inner { display: flex; align-items: center; gap: var(--s4); min-height: 64px; }
.logo { display: inline-flex; align-items: center; gap: var(--s2); font-weight: 800; font-size: 20px; color: var(--c-text); text-decoration: none; }
.logo__mark { color: var(--c-accent); }
.site-nav { display: flex; align-items: center; gap: var(--s3); margin-left: auto; }
.site-nav__link { color: var(--c-text); text-decoration: none; font-weight: 500; }
.site-nav__link.is-active, .site-nav__link:hover { color: var(--c-primary); }
.nav-toggle { display: none; margin-left: auto; font-size: 22px; background: none; border: 0; color: var(--c-text); cursor: pointer; }
.lang-switch { display: inline-flex; border: 1px solid var(--c-border); border-radius: 999px; overflow: hidden; }
.lang-switch__item { padding: 6px 10px; font-size: 13px; text-decoration: none; color: var(--c-muted); }
.lang-switch__item.is-active { background: var(--c-primary); color: var(--c-primary-ink); }
.site-footer { border-top: 1px solid var(--c-border); margin-top: var(--s8); padding: var(--s6) 0; color: var(--c-muted); font-size: 14px; }
@media (max-width: 720px) {
  .nav-toggle { display: block; }
  .site-nav { display: none; position: absolute; left: 0; right: 0; top: 64px; flex-direction: column; align-items: stretch;
    background: var(--c-surface); border-bottom: 1px solid var(--c-border); padding: var(--s4); }
  .site-nav.is-open { display: flex; }
}

/* ============ Секции лендинга ============ */
.hero { padding: var(--s8) 0 var(--s7); background: linear-gradient(180deg, var(--c-surface), var(--c-bg)); }
.hero__title { font-size: clamp(30px, 5vw, 48px); max-width: 820px; letter-spacing: -0.02em; }
.hero__subtitle { font-size: 18px; color: var(--c-muted); max-width: 720px; }
.hero__actions { display: flex; flex-wrap: wrap; gap: var(--s3); margin: var(--s5) 0; }
.hero__stats { color: var(--c-muted); font-size: 14px; }
.section { padding: var(--s7) 0; }
.section--alt { background: var(--c-surface); border-top: 1px solid var(--c-border); border-bottom: 1px solid var(--c-border); }
.section__title { font-size: 28px; margin-bottom: var(--s5); }
.subsection__title { font-size: 18px; margin: var(--s5) 0 var(--s3); }
.steps { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--s4); grid-template-columns: repeat(3, 1fr); }
.step { position: relative; padding-top: var(--s6); }
.step__num { position: absolute; top: var(--s4); left: var(--s5); width: 28px; height: 28px; border-radius: 50%;
  background: var(--c-accent); color: #10151C; font-weight: 800; display: grid; place-items: center; }
.step__title { margin-top: var(--s3); font-size: 18px; }
.cards-grid { display: grid; gap: var(--s4); grid-template-columns: repeat(3, 1fr); }
@media (max-width: 900px) { .steps, .cards-grid { grid-template-columns: 1fr; } }

/* ============ Карточка ============ */
.card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--radius); padding: var(--s5); box-shadow: var(--shadow); }
.result-card__name { font-size: 20px; margin-bottom: var(--s1); }
.result-card__meta { color: var(--c-muted); margin-bottom: var(--s1); }
.result-card__price { font-weight: 700; margin-bottom: var(--s2); }
.result-card__text { margin: var(--s3) 0 0; }

/* ============ Бейджи ============ */
.badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600;
  background: var(--c-neutral-bg); color: var(--c-muted); margin-right: var(--s1); }
.badge--synthetic { background: var(--c-warn-bg); color: var(--c-warn); }
.badge--price_imputed, .badge--city_imputed { background: var(--c-info-bg); color: var(--c-info); }
.badge--price_equals_budget { background: var(--c-bad-bg); color: var(--c-bad); }

/* ============ Баннеры исходов ============ */
.outcomes { list-style: none; padding: 0; margin: 0; display: grid; gap: var(--s3); }
.banner { display: flex; gap: var(--s3); align-items: flex-start; padding: var(--s4); border-radius: var(--radius-sm); border: 1px solid var(--c-border); }
.banner__icon { flex: 0 0 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; font-weight: 800; color: #fff; }
.banner--found { background: var(--c-ok-bg); }      .banner--found .banner__icon { background: var(--c-ok); }
.banner--partial { background: var(--c-warn-bg); }  .banner--partial .banner__icon { background: var(--c-warn); }
.banner--nocat { background: var(--c-info-bg); }    .banner--nocat .banner__icon { background: var(--c-info); }
.banner--none { background: var(--c-bad-bg); }      .banner--none .banner__icon { background: var(--c-bad); }
.banner--invalid { background: var(--c-neutral-bg); } .banner--invalid .banner__icon { background: var(--c-muted); }

/* ============ Цифры и чипы ============ */
.stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: var(--s3); margin: 0; }
.stat { background: var(--c-bg); border: 1px solid var(--c-border); border-radius: var(--radius-sm); padding: var(--s4); }
.stat dt { color: var(--c-muted); font-size: 13px; order: 2; }
.stat dd { margin: 0; font-size: 32px; font-weight: 800; }
@media (max-width: 900px) { .stats { grid-template-columns: repeat(2, 1fr); } }
.chips { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: var(--s2); }
.chip { padding: 6px 12px; border-radius: 999px; background: var(--c-bg); border: 1px solid var(--c-border); font-size: 14px; }
.chip__count { color: var(--c-muted); font-weight: 700; margin-left: var(--s1); }

/* ============ FAQ ============ */
.faq__item { border-bottom: 1px solid var(--c-border); padding: var(--s3) 0; }
.faq__item summary { cursor: pointer; font-weight: 600; }
.faq__item p { margin-top: var(--s2); color: var(--c-muted); }
.faq__cta { margin-top: var(--s5); }

/* ============ Формы (понадобятся в фазах 2–4) ============ */
.form-grid { display: grid; gap: var(--s4); grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
.field { display: flex; flex-direction: column; gap: var(--s1); }
.field label { font-weight: 600; font-size: 14px; }
.field input, .field select, .field textarea { font: inherit; padding: 10px 12px; border-radius: var(--radius-sm);
  border: 1px solid var(--c-border); background: var(--c-surface); color: var(--c-text); }
.field input:focus, .field select:focus, .field textarea:focus { border-color: var(--c-primary); outline: none; box-shadow: 0 0 0 3px rgba(0,150,183,.18); }
.field__hint { color: var(--c-muted); font-size: 13px; }
.field__error { color: var(--c-bad); font-size: 13px; }
.field--invalid input, .field--invalid select { border-color: var(--c-bad); }
.form-card { max-width: 460px; margin: var(--s7) auto; }
.flash { padding: var(--s3) var(--s4); border-radius: var(--radius-sm); margin-bottom: var(--s4); }
.flash--error { background: var(--c-bad-bg); color: var(--c-bad); }
.flash--ok { background: var(--c-ok-bg); color: var(--c-ok); }
```

### 10.16 `app/static/js/app.js`

```javascript
(function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
})();
```

---

## 11. i18n: ключи этой фазы

Главный разработчик кладёт **все** ключи в `ru.json` сразу. Участник 2 копирует в `kk.json` и `en.json` и правит казахский (всё, что помечено «проверить», — сверить с носителем или с KZ-версией ТЗ).

### 11.1 Общие и навигация

| Ключ | RU | KZ | EN |
| --- | --- | --- | --- |
| `meta.description` | Подбор event-подрядчиков с честными объяснениями | Адал түсіндірмесі бар event-мердігерлерді іріктеу | Event contractor matching with honest explanations |
| `common.skip_to_content` | Перейти к содержимому | Мазмұнға өту | Skip to content |
| `nav.menu` | Меню | Мәзір | Menu |
| `nav.search` | Подбор | Іріктеу | Find |
| `nav.how` | Как это работает | Бұл қалай жұмыс істейді | How it works |
| `nav.language` | Язык | Тіл | Language |
| `nav.login` | Войти | Кіру | Log in |
| `nav.register` | Регистрация | Тіркелу | Sign up |
| `nav.account` | Кабинет | Жеке кабинет | Account |
| `nav.logout` | Выйти | Шығу | Log out |
| `footer.text` | Tandau — прототип для HackAlem AI, трек «Креативные индустрии», кейс Firebird. | Tandau — HackAlem AI үшін прототип, «Креативті индустриялар» трегі, Firebird кейсі. | Tandau is a HackAlem AI prototype, Creative Industries track, Firebird case. |
| `footer.api` | API и документация | API және құжаттама | API & docs |
| `app.placeholder.title` | Подбор скоро появится | Іріктеу жақында қосылады | Matching is coming soon |
| `app.placeholder.text` | Эта страница заработает в следующей версии. | Бұл бет келесі нұсқада іске қосылады. | This page will work in the next version. |

### 11.2 Лендинг

| Ключ | RU | KZ | EN |
| --- | --- | --- | --- |
| `landing.hero.title_short` | подбор подрядчиков с объяснениями | түсіндірмесі бар мердігер іріктеу | explained contractor matching |
| `landing.hero.title` | Три подрядчика — и честное объяснение, почему именно они | Үш мердігер — және неге дәл солар екенінің адал түсіндірмесі | Three contractors — and an honest explanation of why |
| `landing.hero.subtitle` | Укажите город, дату, тип мероприятия и бюджет. Мы уберём занятых и неподходящих, а по каждому выбранному объясним, чем он подходит вам — цифрами и фактами из профиля. | Қаланы, күнді, іс-шара түрін және бюджетті көрсетіңіз. Біз бос еместерді және сәйкес келмейтіндерді алып тастаймыз, ал таңдалған әрқайсысының сізге неге сай келетінін сандармен және профильдегі деректермен түсіндіреміз. | Tell us the city, date, event type and budget. We drop the booked and the unsuitable, and explain each pick with numbers and facts from the profile. |
| `landing.hero.cta_primary` | Подобрать без регистрации | Тіркелмей іріктеу | Find without signing up |
| `landing.hero.cta_secondary` | Создать аккаунт | Аккаунт ашу | Create an account |
| `landing.hero.stats` | {profiles} профилей · {categories} категорий · {cities} города · {days} дней календаря | {profiles} профиль · {categories} санат · {cities} қала · күнтізбенің {days} күні | {profiles} profiles · {categories} categories · {cities} cities · {days} calendar days |
| `landing.how.title` | Как это работает | Бұл қалай жұмыс істейді | How it works |
| `landing.how.step1.title` | Параметры заказа | Тапсырыс параметрлері | Your request |
| `landing.how.step1.text` | Город, дата, тип мероприятия, категория и бюджет. По желанию — длительность и язык. | Қала, күн, іс-шара түрі, санат және бюджет. Қаласаңыз — ұзақтығы мен тілі. | City, date, event type, category and budget. Optionally, duration and language. |
| `landing.how.step2.title` | Честные фильтры | Адал сүзгілер | Honest filters |
| `landing.how.step2.text` | Убираем тех, кто занят на дату, не укладывается в бюджет, не берёт ваш формат или язык, — и запоминаем, кого и почему. | Сол күні бос еместерді, бюджетке сыймайтындарды, форматыңызды немесе тіліңізді алмайтындарды алып тастаймыз — кімді және неге екенін сақтаймыз. | We drop anyone booked on the date, over budget, or not taking your format or language — and keep track of who and why. |
| `landing.how.step3.title` | До трёх карточек с объяснением | Түсіндірмесі бар үшке дейін карточка | Up to three explained picks |
| `landing.how.step3.text` | Каждое объяснение опирается на факты: цену и запас бюджета, форматы, языки, часы и цитату из описания. | Әр түсіндірме деректерге сүйенеді: баға мен бюджет қоры, форматтар, тілдер, сағаттар және сипаттамадан үзінді. | Every explanation cites facts: price and budget margin, formats, languages, hours and a quote from the profile. |
| `landing.example.title` | Так выглядит объяснение | Түсіндірме осылай көрінеді | What an explanation looks like |
| `landing.example.query` | Запрос: Алматы · 17 октября · свадьба · ведущий · до 1 000 000 ₸ · казахский · 8 ч | Сұраныс: Алматы · 17 қазан · үйлену тойы · жүргізуші · 1 000 000 ₸ дейін · қазақ тілі · 8 сағ | Request: Almaty · 17 October · wedding · host · up to ₸1,000,000 · Kazakh · 8 h |
| `landing.example.card1` | Свадьбы — её узкий профиль: берёт только свадьбы и тои, по описанию — «356 свадеб» за 13 лет. Цена от 900 000 ₸, запас 100 000 ₸; цена проставлена при подготовке данных — уточните. | Үйлену тойлары — оның тар бейіні: тек үйлену тойы мен той алады, сипаттамасы бойынша — 13 жылда «356 үйлену тойы». Бағасы 900 000 ₸-ден, қор 100 000 ₸; баға деректерді дайындау кезінде қойылған — нақтылаңыз. | Weddings are her niche: she only takes weddings and toi, and her profile mentions “356 weddings” over 13 years. From ₸900,000, leaving ₸100,000 of budget; the price was filled in during data prep, so double-check it. |
| `landing.example.card2` | Единственный из трёх, кто ведёт ещё и на английском, и в описании прямо названы проводы невесты и обряд первых шагов. До 10 ч на площадке — запас 2 ч к вашим 8 ч; цена от 900 000 ₸. | Үшеуінің ішінде ағылшын тілінде де жүргізетін жалғыз маман, сипаттамасында қыз ұзату мен тұсаукесер тікелей аталған. Алаңда 10 сағатқа дейін — сіздің 8 сағатыңызға 2 сағат қор; бағасы 900 000 ₸-ден. | The only one of the three who also hosts in English, and the profile names bride send-off and first-steps ceremonies. Up to 10 h on site, 2 h more than your 8 h; from ₸900,000. |
| `landing.example.card3` | Актёр и телеведущий по описанию, ведёт на казахском. Цена от 1 000 000 ₸ равна бюджету — итог может быть выше; максимум 8 ч, без запаса. | Сипаттамасы бойынша актёр және тележүргізуші, қазақ тілінде жүргізеді. Бағасы 1 000 000 ₸-ден — бюджетке тең, қорытынды жоғары болуы мүмкін; ең көбі 8 сағ, қорсыз. | An actor and TV host per the profile, hosts in Kazakh. From ₸1,000,000, exactly your budget, so the final price may be higher; 8 h max, no slack. |
| `landing.honesty.title` | Если подобрать нельзя — скажем почему | Іріктеу мүмкін болмаса — себебін айтамыз | If there is no match, we tell you why |
| `landing.honesty.found` | Подобрали 3 из 10 ведущих Алматы на 17 октября — остальные заняты, дороже бюджета или не берут свадьбы. | 17 қазанға Алматының 10 жүргізушісінің 3-еуі іріктелді — қалғандары бос емес, бюджеттен қымбат немесе үйлену тойын алмайды. | Found 3 of 10 Almaty hosts for 17 October — the rest are booked, over budget or don’t take weddings. |
| `landing.honesty.nocat` | В Астане декораторов нет — в Алматы их 3, из них 2 синтетических. | Астанада декораторлар жоқ — Алматыда 3, оның 2-еуі синтетикалық. | There are no decorators in Astana — Almaty has 3, 2 of them synthetic. |
| `landing.honesty.none` | 26 декабря 9 из 10 ведущих Алматы заняты, а свободный не ведёт тои. С бюджетом от 900 000 ₸ 27 декабря свободны двое. | 26 желтоқсанда Алматының 10 жүргізушісінің 9-ы бос емес, ал бос жүргізуші той жүргізбейді. 900 000 ₸ бюджетпен 27 желтоқсанда екеуі бос. | On 26 December 9 of 10 Almaty hosts are booked, and the free one doesn’t host toi. With ₸900,000, two are free on 27 December. |
| `landing.stats.title` | Каталог в цифрах | Каталог сандармен | The catalog in numbers |
| `landing.stats.profiles` | профилей | профиль | profiles |
| `landing.stats.categories` | категорий | санат | categories |
| `landing.stats.cities` | города | қала | cities |
| `landing.stats.days` | дней календаря | күнтізбе күні | calendar days |
| `landing.stats.synthetic` | синтетических помечены | синтетикалық белгіленген | synthetic, flagged |
| `landing.categories.title` | Категории | Санаттар | Categories |
| `landing.faq.title` | Вопросы | Сұрақтар | Questions |
| `landing.faq.q1` | Нужна ли регистрация? | Тіркелу қажет пе? | Do I need an account? |
| `landing.faq.a1` | Нет. Подбор работает без входа. Аккаунт нужен, чтобы сохранять историю запросов и избранное. | Жоқ. Іріктеу кірусіз жұмыс істейді. Аккаунт сұраныстар тарихы мен таңдаулыларды сақтау үшін керек. | No. Matching works without signing in. An account lets you keep your search history and favourites. |
| `landing.faq.q2` | Откуда данные? | Деректер қайдан алынған? | Where does the data come from? |
| `landing.faq.a2` | Из анонимизированного каталога 66 подрядчиков, который предоставил Firebird. 13 профилей синтетические — мы их помечаем. | Firebird ұсынған 66 мердігердің анонимделген каталогынан. 13 профиль синтетикалық — біз оларды белгілейміз. | From an anonymised catalog of 66 contractors provided by Firebird. 13 profiles are synthetic, and we flag them. |
| `landing.faq.q3` | Почему именно эти три? | Неге дәл осы үшеуі? | Why these three? |
| `landing.faq.a3` | Мы считаем прозрачный балл: бюджет, специализация, смысл описания, опыт. Разбивку можно раскрыть под каждой карточкой. | Біз ашық балл есептейміз: бюджет, мамандану, сипаттаманың мағынасы, тәжірибе. Толық есебін әр карточканың астынан ашуға болады. | We compute a transparent score from budget fit, specialisation, profile relevance and experience. Expand the breakdown under any card. |
| `landing.faq.q4` | Одинаковый запрос — одинаковый ответ? | Бірдей сұраныс — бірдей жауап па? | Same request, same answer? |
| `landing.faq.a4` | Да. Подбор детерминирован: тот же запрос всегда даёт тот же порядок карточек. | Иә. Іріктеу детерминирленген: бірдей сұраныс әрқашан карточкалардың бірдей ретін береді. | Yes. Matching is deterministic: the same request always returns the same order. |

### 11.3 Карточки, бейджи и значения данных (нужны уже на лендинге)

| Ключ | RU | KZ | EN |
| --- | --- | --- | --- |
| `card.price_from` | от {price} | {price}-ден бастап | from {price} |
| `badge.synthetic` | синтетический профиль | синтетикалық профиль | synthetic profile |
| `badge.price_imputed` | цена ориентировочная | баға шамамен | estimated price |
| `badge.city_imputed` | город уточняется | қала нақтыланады | city unconfirmed |
| `badge.price_equals_budget` | цена «от» = бюджет | «бастап» бағасы = бюджет | “from” price = budget |

Значения данных — ключи `data.<kind>.<значение из CSV>` для всех 17 категорий, 6 форматов, 3 языков, 3 городов. Полные переводы — в `01_REFERENCE.md`, раздел 5 (глоссарий). Пример для `ru.json`:

```json
{
  "data.category.Ведущий": "Ведущий",
  "data.category.Ведущий церемонии": "Ведущий церемонии",
  "data.format.свадьба": "свадьба",
  "data.format.день рождения": "день рождения",
  "data.city.Зарубежье": "Зарубежье",
  "data.language.казахский": "казахский"
}
```

и для `kk.json`: `"data.category.Ведущий": "Жүргізуші"`, `"data.format.свадьба": "үйлену тойы"`, `"data.city.Зарубежье": "Шетел"`, `"data.language.казахский": "қазақ"` и так далее.

---

## 12. Тесты

### 12.1 `tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def catalog():
    return app.state.catalog
```

### 12.2 `tests/test_data.py`

```python
from matcher.data import WINDOW_END, WINDOW_START


def test_row_count_and_unique_ids(catalog):
    assert len(catalog.contractors) == 66
    assert len(catalog.by_id) == 66


def test_flags_parsed_from_true_false(catalog):
    assert sum(c.synthetic for c in catalog.contractors) == 13
    assert sum(c.price_imputed for c in catalog.contractors) == 18
    assert sum(c.city_imputed for c in catalog.contractors) == 8


def test_categories_are_list_elements(catalog):
    assert len(catalog.categories) == 17
    hosts = [c for c in catalog.contractors if c.has_category("Ведущий")]
    ceremony = [c for c in catalog.contractors if c.has_category("Ведущий церемонии")]
    assert len(hosts) == 15 and len(ceremony) == 3


def test_max_hours_empty_is_none(catalog):
    assert sum(c.max_hours is None for c in catalog.contractors) == 9


def test_busy_dates_inside_window(catalog):
    for c in catalog.contractors:
        assert all(WINDOW_START <= d <= WINDOW_END for d in c.busy_dates), c.id


def test_category_city_counts(catalog):
    assert catalog.category_city_counts["Ведущий"] == {"Алматы": 10, "Астана": 5}
    assert "Астана" not in catalog.category_city_counts["Декоратор"]
```

### 12.3 `tests/test_pages.py`

```python
def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json() == {"status": "ok", "profiles": 66}


def test_meta(client):
    data = client.get("/api/meta").json()
    assert len(data["categories"]) == 17
    assert data["window"] == {"start": "2026-09-23", "end": "2026-12-31", "days": 100}
    assert data["stats"]["synthetic"] == 13


def test_landing_ru(client):
    r = client.get("/?lang=ru")
    assert r.status_code == 200
    assert "Tandau" in r.text and 'lang="ru"' in r.text


def test_landing_kk_and_cookie(client):
    r = client.get("/?lang=kk")
    assert 'lang="kk"' in r.text
    assert r.cookies.get("lang") == "kk" or "lang=kk" in r.headers.get("set-cookie", "")


def test_lang_switch_redirect(client):
    r = client.get("/lang/en", follow_redirects=False)
    assert r.status_code == 303 and "lang=en" in r.headers.get("set-cookie", "")
```

### 12.4 Ручной чек-лист (2 минуты)

- [ ] `python run.py` без `.env` — стартует, в `var/` появился `secret_key`
- [ ] `/` на ширине 375px: меню сворачивается, карточки в одну колонку
- [ ] Рус → Қаз → Eng: заголовки меняются, `<html lang>` меняется, после перехода на `/app` язык сохраняется
- [ ] Цифры на лендинге: 66 · 17 · 3 · 100 · 13
- [ ] `/docs` открывается, видны `/healthz` и `/api/meta`
- [ ] В тёмной теме ОС текст читается

---

## 13. Критерии приёмки фазы

- [ ] Структура каталогов совпадает с мастер-планом (+ `app/web.py`)
- [ ] `pip install -r requirements.txt && python run.py` — работает на чистом venv
- [ ] Загрузчик: 66 строк, 13/18/8 флагов, 17 категорий, 9 пустых `max_hours`
- [ ] Лендинг: hero, «как это работает», пример карточек, честность, цифры из данных, FAQ, подвал
- [ ] Переключатель языка на всех страницах, cookie на год
- [ ] `/healthz`, `/api/meta` отвечают по контракту
- [ ] `pytest -q` зелёный
- [ ] Два коммита запушены до 14:50

---

## 14. Коммиты

| Когда | Сообщение | Что внутри |
| --- | --- | --- |
| ~14:30 | `feat: skeleton, catalog loader and meta api` | run.py, config, data, i18n, web, main, api, тесты данных |
| ~14:50 | `feat: landing page with live catalog stats and language switch` | шаблоны, CSS, JS, ru.json, test_pages |
| параллельно | `i18n: kk/en dictionaries for landing` (Участник 2) | kk.json, en.json |

---

## 15. Риски и что режем

| Риск | Что делаем |
| --- | --- |
| `TemplateResponse` ругается на сигнатуру | Старый Starlette: `templates.TemplateResponse(name, {"request": request, **ctx})`. Новый (в requirements) — `TemplateResponse(request, name, ctx)` |
| Кириллица в ключах JSON | Файлы UTF-8, `json.loads(path.read_text(encoding="utf-8"))` |
| `python-multipart` не установлен | Он в requirements; без него упадут формы фазы 2 |
| Вёрстка съедает время | Жёсткий тайм-бокс 14:30–14:45; при превышении выбросить пример карточек и FAQ |
| Участник 2 ещё не прислал kk/en | Не ждать: `translate` откатывается на `ru` |

---

## 16. Промпты для Codex

**Промпт 1 — каркас и данные (14:14)**

```text
Создай Python-проект по структуре из docs/00_MASTER_PLAN.md (раздел 3). Стек: FastAPI, Uvicorn, Jinja2, SessionMiddleware, без БД на этом шаге. Реализуй ровно эти файлы по коду из docs/PHASE_1_FOUNDATION_AND_LANDING.md, разделы 10.1–10.8: run.py, .gitignore, requirements.txt (из мастер-плана), app/config.py, matcher/models.py (Contractor), matcher/data.py (load_catalog, Catalog.stats/category_rows/meta), app/i18n.py, app/web.py, app/main.py, app/routes/pages.py, app/routes/api.py. Данные: data/hackathon-dataset-anonymized.csv — булевы флаги записаны как True/False, списки через '|', пустой max_hours = None. Категории сравнивать по элементу списка. Затем напиши tests/conftest.py и tests/test_data.py из раздела 12 и убедись, что pytest проходит.
```

**Промпт 2 — лендинг (14:30)**

```text
Сделай серверный лендинг на Jinja2 по docs/PHASE_1_FOUNDATION_AND_LANDING.md: base.html, partials/header.html, partials/footer.html, partials/lang_switch.html, landing.html (разделы 10.10–10.14), static/css/app.css и static/js/app.js (10.15–10.16). Все тексты — только через t('ключ'); ключи и русские значения возьми из раздела 11 и запиши в app/i18n/ru.json. Значения из данных (категории, города) выводи через label(kind, value). Цифры статистики бери из catalog.stats(), не хардкодь. Добавь tests/test_pages.py из раздела 12.3. Без внешних CDN, шрифтов и картинок из интернета.
```

**Промпт 3 — проверка (14:46)**

```text
Прогони pytest -q и исправь падения, не меняя имена файлов, функций и маршрутов. Проверь, что GET /, /?lang=kk, /lang/en, /healthz, /api/meta, /app отвечают без ошибок, а в /api/meta 17 категорий и stats.synthetic = 13.
```

---

## 17. Передача в фазу 2

Должно работать до начала фазы 2:

- `render(request, "…html", **ctx)` из `app/web.py` — все новые страницы рендерятся только через него (даёт `t`, `label`, `csrf`, `user`, `lang`).
- `ensure_csrf()` уже кладёт токен в сессию — формы регистрации используют `{{ csrf }}`.
- Стили форм (`.form-card`, `.field`, `.field__error`, `.flash`) уже в `app.css`.
- В шапке есть ссылки на `/login` и `/register` — фаза 2 их оживляет.
