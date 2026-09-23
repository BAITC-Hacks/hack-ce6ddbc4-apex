"""Ищет сильные демо-запросы по данным (город × категория × формат × дата окна).

Печатает: плотные категории с 4–6 прошедшими, редкие с 1–2, none_match, пары соседних дат с разной
выдачей (разница — только занятость: бюджет = максимальная цена в выборке, язык и часы не заданы),
и пары город×категория без профилей (no_category_in_city).

Запуск из корня репозитория:  python scripts/find_demo_queries.py [--city Алматы] [--saturdays] [--limit 6]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from matcher.data import CITIES, EVENT_FORMATS, WINDOW_DAYS, WINDOW_START, load_catalog  # noqa: E402
from matcher.engine import recommend  # noqa: E402
from matcher.explain import fmt_kzt  # noqa: E402
from matcher.filters import check  # noqa: E402
from matcher.models import SearchRequest  # noqa: E402

DENSE_MIN_POOL = 8          # «плотная» категория: ≥ 8 профилей в городе (Ведущий, Фотограф, Банкетный зал)
RARE_MAX_POOL = 3           # «редкая»: ≤ 3 профилей в городе


def key_tr(key: str, **kwargs) -> str:
    return key               # тексты скрипту не нужны — только статусы и id


def window_dates(saturdays: bool) -> list[str]:
    start = date.fromisoformat(WINDOW_START)
    days = [start + timedelta(days=i) for i in range(WINDOW_DAYS)]
    return [d.isoformat() for d in days if not saturdays or d.weekday() == 5]


def link(req: SearchRequest) -> str:
    return "/app?" + urlencode(req.to_query())


def show(title: str, rows: list, limit: int, fmt) -> None:
    print(f"\n== {title}: {len(rows)} ==")
    for row in rows[:limit]:
        print(fmt(row))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--city", choices=CITIES)
    ap.add_argument("--saturdays", action="store_true", help="только субботы (соседние субботы — пары дат)")
    ap.add_argument("--limit", type=int, default=6)
    args = ap.parse_args()

    catalog = load_catalog(ROOT / "data" / "hackathon-dataset-anonymized.csv")
    dates = window_dates(args.saturdays)
    dense, rare, empty, pairs, nocat = [], [], [], [], []
    for city in ([args.city] if args.city else list(CITIES)):
        for category in catalog.categories:
            pool = catalog.in_category_city(category, city)
            if not pool:
                nocat.append((city, category, catalog.category_city_counts[category]))
                continue
            budget = max(c.price_from_kzt for c in pool)
            for fmt in EVENT_FORMATS:
                if not any(fmt in c.event_formats for c in pool):
                    continue                     # формат не берёт никто — это не про занятость
                prev = None
                for d in dates:
                    req = SearchRequest(city=city, date=d, event_type=fmt, category=category, budget_kzt=budget)
                    ok = [c.id for c in pool if not check(c, req)]
                    if len(pool) >= DENSE_MIN_POOL and 4 <= len(ok) <= 6:
                        dense.append((req, len(pool), ok))
                    elif len(pool) <= RARE_MAX_POOL and 1 <= len(ok) <= 2:
                        rare.append((req, len(pool), ok))
                    elif not ok:
                        empty.append((req, len(pool), ok))
                    if prev and prev[1] and ok and set(prev[1]) != set(ok):
                        pairs.append((req, prev[0], prev[1], ok))
                    prev = (d, ok)

    def row_fmt(row):
        req, pool_n, ok = row
        status = recommend(catalog, req, key_tr).status          # сверка с движком
        return (f"{req.city} · {req.category} · {req.event_type} · {req.date} · до {fmt_kzt(req.budget_kzt)}"
                f" → {status}, прошли {len(ok)} из {pool_n}: {', '.join(ok) or '—'}\n    {link(req)}")

    def pair_fmt(row):
        req, prev_date, before, after = row
        came, left = sorted(set(after) - set(before)), sorted(set(before) - set(after))
        return (f"{req.city} · {req.category} · {req.event_type}: {prev_date} → {req.date}"
                f" | вошли: {', '.join(came) or '—'} | выпали (заняты): {', '.join(left) or '—'}")

    dense.sort(key=lambda r: (-r[1], r[0].date, r[0].category))
    rare.sort(key=lambda r: (r[0].date, r[0].category))
    empty.sort(key=lambda r: (-r[1], r[0].date))
    pairs.sort(key=lambda r: (-len(set(r[2]) ^ set(r[3])), r[0].date))
    show("Плотные категории, прошли 4–6", dense, args.limit, row_fmt)
    show("Редкие категории, прошли 1–2", rare, args.limit, row_fmt)
    show("none_match: кандидаты есть, прошло 0", empty, args.limit, row_fmt)
    show("Пары соседних дат с разной выдачей", pairs, args.limit, pair_fmt)
    show("no_category_in_city", nocat, 50,
         lambda r: f"{r[0]} · {r[1]} → нет; есть: " + ", ".join(f"{k}: {v}" for k, v in sorted(r[2].items())))


if __name__ == "__main__":
    main()
