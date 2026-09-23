"""Объяснения v1: атомы-факты из полей профиля → 1–2 предложения. Тексты — только через tr (ключи explain.*)."""
from __future__ import annotations

from typing import Callable, Optional, Sequence

from .data import EVENT_FORMATS, LANGUAGES
from .models import Atom, Contractor, SearchRequest

Translator = Callable[..., str]          # tr(key, **kwargs) -> str; движок не импортирует app/

ATOM_WEIGHTS = {"budget": 0.9, "format_focus": 0.8, "language": 0.7, "duration": 0.6, "flag": 0.5, "contrast": 0.4}
INFO_WEIGHT = 0.2                        # «для сведения»: язык/часы, которых не было в запросе
TYPE_ORDER = ("budget", "format_focus", "language", "duration", "contrast", "flag")

STOP_PHRASES = (   # сверено с таблицей «Запрещённые фразы» в ISSUE_i18n_and_minor_tasks.md; «ё» → «е»
    "отличный выбор", "отличный вариант", "лучший выбор", "лучший вариант", "идеальн", "прекрасный вариант",
    "отлично подойдет", "профессионал своего дела", "высокое качество", "индивидуальный подход",
    "на высшем уровне", "незабываем", "не пожалеете", "для вашего мероприятия", "для вашего праздника", "великолепн",
    "тамаша таңдау", "керемет таңдау", "ең жақсы таңдау", "ең жақсы нұсқа", "мінсіз", "тамаша нұсқа",
    "тамаша сай келеді", "өз ісінің шебері", "жоғары сапа", "жеке көзқарас", "жоғары деңгейде", "ұмытылмас",
    "өкінбейсіз", "іс-шараңызға тамаша",
    "great choice", "excellent choice", "best choice", "best option", "perfect", "ideal", "great option",
    "true professional", "high quality", "individual approach", "top-notch", "unforgettable", "won't regret",
    "for your event",
)


def has_stop_phrase(text: str) -> bool:
    low = text.lower().replace("ё", "е")
    return any(p in low for p in STOP_PHRASES)


def fmt_kzt(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₸"


def label(tr: Translator, kind: str, value: Optional[str]) -> str:
    if not value:
        return ""
    key = f"data.{kind}.{value}"
    text = tr(key)
    return value if text == key else text


def join_human(items: Sequence[str], tr: Translator) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {tr('explain.and')} " + items[-1]


def fmt_date(date_iso: str, tr: Translator) -> str:
    _, month, day = (int(x) for x in date_iso.split("-"))
    months = [m.strip() for m in tr("search.date.months").split(",")]
    month_name = months[month - 1] if len(months) == 12 else f"{month:02d}"
    return tr("search.date.day_month", day=day, month=month_name)


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def _canon(values: Sequence[str], order: Sequence[str]) -> list[str]:
    return sorted(values, key=lambda v: order.index(v) if v in order else len(order))


def format_plural(value: str, tr: Translator) -> str:
    key = f"explain.format_pl.{value}"
    text = tr(key)
    return label(tr, "format", value) if text == key else text


def badges_for(c: Contractor, req: SearchRequest) -> list[str]:
    badges = [flag for flag in ("synthetic", "price_imputed", "city_imputed") if getattr(c, flag)]
    if c.price_from_kzt == req.budget_kzt:
        badges.append("price_equals_budget")
    return badges


def build_atoms(c: Contractor, req: SearchRequest, tr: Translator) -> list[Atom]:
    atoms: list[Atom] = []
    # 1. Бюджет — всегда (в каждом объяснении есть число)
    if c.price_from_kzt == req.budget_kzt:
        text = tr("explain.budget.equal", price=fmt_kzt(c.price_from_kzt))
    else:
        text = tr("explain.budget.margin", price=fmt_kzt(c.price_from_kzt),
                  pct=round(c.price_from_kzt * 100 / req.budget_kzt),
                  margin=fmt_kzt(req.budget_kzt - c.price_from_kzt))
    atoms.append(Atom("budget", text, weight=ATOM_WEIGHTS["budget"]))
    # 2. Фокус на формате: узкий (1–2 формата) или широкий профиль
    formats = [format_plural(f, tr) for f in _canon(c.event_formats, EVENT_FORMATS)]
    key = "explain.format.narrow" if len(formats) <= 2 else "explain.format.broad"
    atoms.append(Atom("format_focus", tr(key, formats=join_human(formats, tr)), weight=ATOM_WEIGHTS["format_focus"]))
    # 3. Язык: запрошенный (+ дополнительные) или список, если языков больше одного
    langs = _canon(c.languages, LANGUAGES)
    if req.language:
        others = [label(tr, "language", l) for l in langs if l != req.language]
        lang_label = label(tr, "language", req.language)
        text = (tr("explain.language.requested_plus", language=lang_label, others=join_human(others, tr))
                if others else tr("explain.language.requested", language=lang_label))
        atoms.append(Atom("language", text, weight=ATOM_WEIGHTS["language"]))
    elif len(langs) > 1:
        text = tr("explain.language.list", languages=join_human([label(tr, "language", l) for l in langs], tr))
        atoms.append(Atom("language", text, weight=INFO_WEIGHT))
    # 4. Длительность: запас часов / ровно / без ограничения
    if req.duration_h:
        if c.max_hours is None:
            atoms.append(Atom("duration", tr("explain.duration.unbounded"), weight=ATOM_WEIGHTS["duration"]))
        elif c.max_hours > req.duration_h:
            atoms.append(Atom("duration", tr("explain.duration.slack", max=c.max_hours, hours=req.duration_h,
                                              slack=c.max_hours - req.duration_h), weight=ATOM_WEIGHTS["duration"]))
        else:
            atoms.append(Atom("duration", tr("explain.duration.exact", max=c.max_hours), weight=ATOM_WEIGHTS["duration"]))
    elif c.max_hours is not None:
        atoms.append(Atom("duration", tr("explain.duration.info", max=c.max_hours), weight=INFO_WEIGHT))
    # 5. Флаги данных — честность важнее краткости
    if c.synthetic:
        atoms.append(Atom("flag", tr("explain.flag.synthetic"), weight=ATOM_WEIGHTS["flag"]))
    if c.price_imputed and c.city_imputed:
        atoms.append(Atom("flag", tr("explain.flag.price_city_imputed"), weight=ATOM_WEIGHTS["flag"]))
    elif c.price_imputed:
        atoms.append(Atom("flag", tr("explain.flag.price_imputed"), weight=ATOM_WEIGHTS["flag"]))
    elif c.city_imputed:
        atoms.append(Atom("flag", tr("explain.flag.city_imputed"), weight=ATOM_WEIGHTS["flag"]))
    return [a for a in atoms if not has_stop_phrase(a.text)]


def mark_unique(atom_lists: list[list[Atom]]) -> None:
    texts = [{a.text for a in atoms} for atoms in atom_lists]
    for i, atoms in enumerate(atom_lists):
        others = set().union(*(t for j, t in enumerate(texts) if j != i))
        for a in atoms:
            a.unique = a.text not in others


def contrast_atoms(i: int, cards: Sequence[Contractor], tr: Translator) -> list[Atom]:
    """Контраст по рангу среди показанных карточек — только строго истинные утверждения."""
    c, others, n = cards[i], [o for j, o in enumerate(cards) if j != i], len(cards)
    w = ATOM_WEIGHTS["contrast"]
    out: list[Atom] = []
    if all(c.price_from_kzt < o.price_from_kzt for o in others):
        out.append(Atom("contrast", tr("explain.contrast.cheapest", n=n), weight=w))
    if c.max_hours is not None and all(o.max_hours is not None and c.max_hours > o.max_hours for o in others):
        out.append(Atom("contrast", tr("explain.contrast.most_hours", n=n), weight=w))
    if all(len(c.event_formats) < len(o.event_formats) for o in others):
        out.append(Atom("contrast", tr("explain.contrast.narrowest", n=n), weight=w))
    for lang in LANGUAGES:
        if lang in c.languages and all(lang not in o.languages for o in others):
            out.append(Atom("contrast", tr("explain.contrast.only_language", n=n,
                                           language=label(tr, "language", lang)), weight=w))
            break
    return out


def compose_explanation(atoms: list[Atom], tr: Translator) -> str:
    """1-е предложение — самый весомый уникальный атом; 2-е — бюджет + ещё один факт + флаги."""
    if not atoms:
        return ""
    rank = {t: i for i, t in enumerate(TYPE_ORDER)}
    ordered = sorted(atoms, key=lambda a: (not a.unique, -a.weight, rank.get(a.type, len(rank))))
    lead, rest = ordered[0], ordered[1:]
    second = [a for a in rest if a.type == "budget"]
    second += [a for a in rest if a.type not in ("budget", "flag")][:1]
    second += [a for a in rest if a.type == "flag"]
    text = _cap(lead.text) + "."
    if second:
        text += " " + _cap("; ".join(a.text for a in second)) + "."
    return text


def explain_cards(cards: Sequence[Contractor], req: SearchRequest, scores: Sequence[float],
                  tr: Translator) -> list[tuple[list[Atom], str]]:
    atom_lists = [build_atoms(c, req, tr) for c in cards]
    mark_unique(atom_lists)
    for i, atoms in enumerate(atom_lists):
        if len(cards) > 1 and not any(a.unique for a in atoms):
            extra = contrast_atoms(i, cards, tr) or [Atom("contrast", tr(
                "explain.contrast.rank", rank=i + 1, n=len(cards), score=f"{scores[i]:.2f}"),
                weight=ATOM_WEIGHTS["contrast"])]
            atoms.append(extra[0])
    mark_unique(atom_lists)
    return [(atoms, compose_explanation(atoms, tr)) for atoms in atom_lists]
