"""Объяснения v2: факты → атомы → контраст внутри выдачи → 1–2 предложения через tr (RU/KZ/EN).

Предложение 1 — сильнейший уникальный атом + подтверждение другим фактом.
Предложение 2 — цифры (цена и запас, часы) + флаги честности. Цитаты не переводятся.
"""
from __future__ import annotations

import itertools
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from .evidence import find_quote, load_enriched
from .facts import FORMAT_PATTERNS, LANGUAGE_PATTERNS, Facts, normalize
from .models import Atom, Card, Contractor, Rejection, SearchRequest
from .scoring import (FORMAT_FAMILY, ScoreBreakdown, ScoreContext, focus, hours_slack,
                      relevant_mentions, venues_of)

Tr = Callable[..., str]
ENRICHED_PATH = str(Path(__file__).resolve().parent.parent / "data" / "enriched.json")
REASON_ORDER = ("busy", "format", "budget", "language", "duration")

STOP_PHRASES = (
    "отличный выбор", "идеальный выбор", "лучший выбор", "прекрасный выбор", "отличный вариант",
    "для вашего мероприятия", "для вашего праздника", "незабываем", "профессионал своего дела",
    "высокое качество", "высокий уровень", "на высшем уровне", "индивидуальный подход", "лучшие в городе",
    "great choice", "perfect choice", "perfect fit", "for your event", "unforgettable", "top quality",
    "тамаша таңдау", "керемет таңдау", "іс-шараңыз үшін",
)
PERSONAL_MARKERS = ("женат", "замужем", "двое детей", "трое детей", "есть дети", "мой муж", "моя жена", "супруг")
W = {  # сила атома при выборе первого предложения
    "contrast.language": 1.0, "contrast.cheapest": 0.95, "contrast.experience": 0.9,
    "contrast.slack": 0.88, "contrast.focus": 0.85, "contrast.venue": 0.85,
    "mentions.unique": 0.75, "experience.unique": 0.65, "quote.hit": 0.55, "venue": 0.5,
    "focus": 0.45, "experience": 0.45, "mentions": 0.4, "focus.share": 0.35, "quote": 0.3,
    "language": 0.3, "budget": 0.2, "duration": 0.2, "flag": 0.0,
}
GROUP_ORDER = ("language", "budget", "experience", "duration", "focus", "venue", "mentions", "quote", "flag")
LANG_CONTRAST_ORDER = ("английский", "казахский", "русский")


# ---------- форматирование (числа не переводятся, слова — через tr) ----------

def fmt_kzt(value: int, lang: str = "ru") -> str:
    digits = f"{value:,}"
    return f"₸{digits}" if lang == "en" else digits.replace(",", " ") + " ₸"


def fmt_date(iso: str, tr: Tr) -> str:
    return tr("explain.date", day=int(iso[8:10]), month=tr(f"explain.month.{int(iso[5:7])}"))


def fmt_list(items: list[str], tr: Tr) -> str:
    items = [x for x in items if x]
    if len(items) < 2:
        return "".join(items)
    return ", ".join(items[:-1]) + f" {tr('explain.and')} " + items[-1]


def plural(forms: str, n: int, lang: str) -> str:
    """forms = «год|года|лет» (ru), «year|years» (en), «жыл» (kk)."""
    parts = forms.split("|")
    if lang == "ru" and len(parts) == 3:
        if n % 10 == 1 and n % 100 != 11:
            return parts[0]
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            return parts[1]
        return parts[2]
    if lang == "en" and len(parts) >= 2:
        return parts[0] if n == 1 else parts[1]
    return parts[0]


def count_text(n: int, plus: bool, noun_key: str, tr: Tr, lang: str) -> str:
    return f"{n}{'+' if plus else ''} {plural(tr(noun_key), n, lang)}"


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


# ---------- атомы ----------

@dataclass
class Draft:
    type: str       # тип Atom: budget|format_focus|language|duration|quote|experience|venue_multi|flag|contrast
    group: str      # о каком факте: один факт не повторяется в двух местах объяснения
    text: str
    unique: bool = False
    weight: float = 0.0
    topics: frozenset = frozenset()   # о чём ещё говорит атом (цитата про язык → «language»)

    def atom(self) -> Atom:
        return Atom(type=self.type, text=self.text, unique=self.unique, weight=round(self.weight, 2))


def experience_text(f: Facts, tr: Tr, lang: str) -> str:
    events = ""
    if f.events_count:
        events = count_text(f.events_count, f.events_plus, f"explain.noun.{f.events_noun}", tr, lang)
        if f.events_period == "month":
            events += " " + tr("explain.per_month")
    parts = []
    if f.years_min and events:
        parts = [count_text(f.years_min, f.years_plus, "explain.noun.year", tr, lang), events]
    elif f.years_min:
        parts = [tr("explain.exp.years", years=count_text(f.years_min, f.years_plus, "explain.noun.year", tr, lang))]
    elif events:
        parts = [events]
    if f.audience_max:
        parts.append(tr("explain.exp.audience", n=f.audience_max))
    return tr("explain.exp.tail", facts=", ".join(parts)) if parts else ""


def build_atoms(c: Contractor, req: SearchRequest, ctx: ScoreContext, tr: Tr) -> dict[str, Draft]:
    lang, f = req.lang, ctx.facts[c.id]
    d: dict[str, Draft] = {}
    price, margin = fmt_kzt(c.price_from_kzt, lang), req.budget_kzt - c.price_from_kzt
    d["budget"] = Draft("budget", "budget", tr("explain.budget.margin", price=price, margin=fmt_kzt(margin, lang))
                        if margin > 0 else tr("explain.budget.equal", price=price), weight=W["budget"])
    family = FORMAT_FAMILY.get(req.event_type, (req.event_type,))
    fv = focus(c, req)
    if fv >= 0.999:
        formats = fmt_list([tr(f"data.format_pl.{x}") for x in c.event_formats], tr)
        d["focus"] = Draft("format_focus", "focus", tr("explain.focus.only", formats=formats), weight=W["focus"])
    elif fv >= 0.5:
        own = [x for x in c.event_formats if x in family]
        d["focus"] = Draft("format_focus", "focus", tr("explain.focus.share", part=len(own), total=len(c.event_formats),
                           formats=fmt_list([tr(f"data.format_pl.{x}") for x in own], tr)), weight=W["focus.share"])
    mentions = relevant_mentions(f, req)
    if mentions:
        items = fmt_list([tr(f"explain.tradition.{m}") for m in mentions], tr)
        d["mentions"] = Draft("format_focus", "mentions", tr("explain.focus.mentions", items=items), weight=W["mentions"])
    if req.language:
        langs = [req.language] + [x for x in c.languages if x != req.language]
        key = "explain.language.works_one" if len(langs) == 1 else "explain.language.works_many"
        d["language"] = Draft("language", "language",
                              tr(key, langs=fmt_list([tr(f"data.language_prep.{x}") for x in langs], tr)), weight=W["language"])
    if req.duration_h:
        slack = hours_slack(c, req)
        if slack is None:
            text = tr("explain.duration.unbound")
        elif slack > 0:
            text = tr("explain.duration.slack", max=c.max_hours, slack=slack, dur=req.duration_h)
        else:
            text = tr("explain.duration.exact", max=c.max_hours)
        d["duration"] = Draft("duration", "duration", text, weight=W["duration"])
    exp = experience_text(f, tr, lang)
    if exp:
        d["experience"] = Draft("experience", "experience", exp, weight=W["experience"])
    venues = venues_of(c)
    if len(venues) >= 2:
        names = fmt_list([tr(f"data.category.{v}").lower() for v in venues], tr)
        d["venue"] = Draft("venue_multi", "venue", tr("explain.venue_multi", venues=names), weight=W["venue"])
    exclude = (f.evidence("years"), f.evidence("events")) if exp else ()
    quote, qscore = find_quote(c.description, ctx.query, ctx.index, banned=STOP_PHRASES + PERSONAL_MARKERS,
                               exclude=tuple(x for x in exclude if x))
    if not quote:  # (опц.) обогащение: основание — тоже точная цитата из описания
        evidence = (load_enriched(ENRICHED_PATH).get(c.id, {}).get("specialization") or {}).get("evidence", "")
        quote = evidence if evidence and evidence in c.description and len(evidence.split()) <= 12 else ""
    if quote:
        qn = normalize(quote)
        topics = {"language" for _, p in LANGUAGE_PATTERNS if p.search(qn)}
        topics |= {"mentions" for _, p in FORMAT_PATTERNS if p.search(qn)}
        d["quote"] = Draft("quote", "quote", tr("explain.quote", quote=quote),
                           weight=W["quote.hit"] if qscore > 0 else W["quote"], topics=frozenset(topics))
    for flag in ("synthetic", "price_imputed", "city_imputed"):
        if getattr(c, flag):
            d[f"flag.{flag}"] = Draft("flag", "flag", tr(f"explain.flag.{flag}"), weight=W["flag"])
    return d


def _upgrade(draft: Optional[Draft], text: str, weight: float) -> None:
    if draft:
        draft.type, draft.text, draft.unique, draft.weight = "contrast", text, True, weight


def _apply_contrasts(shown: list[Contractor], drafts: dict[str, dict[str, Draft]],
                     req: SearchRequest, ctx: ScoreContext, tr: Tr) -> None:
    """Уникальность — среди показанных карточек; экстремумы — среди всех подходящих, иначе среди показанных."""
    n, pool = len(shown), ctx.pool
    if n < 2:
        return
    of_shown = tr(f"explain.of_n.{n}")
    of_pool = tr("explain.of_pool", n=len(pool)) if len(pool) > n else of_shown

    for c in shown:  # единственный с дополнительным языком
        for lang_value in LANG_CONTRAST_ORDER:
            if lang_value == req.language or lang_value not in c.languages:
                continue
            in_pool = sum(lang_value in p.languages for p in pool)
            in_shown = sum(lang_value in s.languages for s in shown)
            scope = of_pool if in_pool == 1 else of_shown if in_shown == 1 else None
            if scope:
                drafts[c.id]["contrast.language"] = Draft(
                    "contrast", "language", tr("explain.contrast.only_language", scope=scope,
                                               language=tr(f"data.language_prep.{lang_value}")),
                    unique=True, weight=W["contrast.language"])
                break

    shown_ids = {c.id for c in shown}

    def holder(values: dict, pick, ok=lambda v: True) -> tuple[Optional[str], Optional[str]]:
        """Строгий экстремум: сначала среди всех подходящих, иначе среди показанных."""
        for scope_ids, scope in ((None, of_pool), (shown_ids, of_shown)):
            vals = {k: v for k, v in values.items() if scope_ids is None or k in scope_ids}
            if len(vals) >= 2:
                best = pick(vals.values())
                winners = [k for k, v in vals.items() if v == best]
                if len(winners) == 1 and winners[0] in shown_ids and ok(best):
                    return winners[0], scope
        return None, None

    cid, scope = holder({p.id: p.price_from_kzt for p in pool}, min)                      # самый доступный
    if cid:
        base = drafts[cid]["budget"]
        _upgrade(base, tr("explain.contrast.cheapest", scope=scope, base=base.text), W["contrast.cheapest"])
    slacks = {p.id: hours_slack(p, req) for p in pool if hours_slack(p, req) is not None}    # запас по часам
    cid, scope = holder(slacks, max, ok=lambda v: v > 0)
    if cid and "duration" in drafts[cid]:
        base = drafts[cid]["duration"]
        _upgrade(base, tr("explain.contrast.most_slack", scope=scope, base=base.text), W["contrast.slack"])
    years = {p.id: ctx.facts[p.id].years_min for p in pool if ctx.facts[p.id].years_min}     # опыт по описанию
    cid, scope = holder(years, max)
    if cid and "experience" in drafts[cid]:
        base = drafts[cid]["experience"]
        _upgrade(base, tr("explain.contrast.most_experienced", scope=scope, base=base.text), W["contrast.experience"])
    with_exp = [c.id for c in shown if "experience" in drafts[c.id]]
    if len(with_exp) == 1 and drafts[with_exp[0]]["experience"].type != "contrast":
        drafts[with_exp[0]]["experience"].unique = True
        drafts[with_exp[0]]["experience"].weight = W["experience.unique"]

    focus_vals = {c.id: focus(c, req) for c in shown}  # узкий профиль
    top = max(focus_vals.values())
    leaders = [cid for cid, v in focus_vals.items() if v == top]
    if len(leaders) == 1 and "focus" in drafts[leaders[0]]:
        base = drafts[leaders[0]]["focus"]
        if top >= 0.999:
            _upgrade(base, tr("explain.contrast.narrowest", scope=of_shown, base=base.text), W["contrast.focus"])
        else:
            base.unique = True

    with_mentions = [c.id for c in shown if "mentions" in drafts[c.id]]  # традиции названы в тексте
    if len(with_mentions) == 1:
        drafts[with_mentions[0]]["mentions"].unique = True
        drafts[with_mentions[0]]["mentions"].weight = W["mentions.unique"]

    for c in shown:  # площадка: единственная с отелем / загородной площадкой
        for v in venues_of(c):
            if v != req.category and sum(v in s.categories for s in shown) == 1:
                drafts[c.id]["contrast.venue"] = Draft(
                    "contrast", "venue", tr("explain.contrast.only_venue", scope=of_shown,
                                            venue=tr(f"data.category.{v}").lower()),
                    unique=True, weight=W["contrast.venue"])
                break

    for kind, value in (("budget", lambda c: c.price_from_kzt), ("duration", lambda c: hours_slack(c, req)),
                        ("quote", lambda c: drafts[c.id]["quote"].text if "quote" in drafts[c.id] else None)):
        for c in shown:  # флаг unique для остальных атомов: значение не совпадает ни с одной другой карточкой
            if kind in drafts[c.id] and drafts[c.id][kind].type != "contrast":
                drafts[c.id][kind].unique = all(value(s) != value(c) for s in shown if s.id != c.id)


def compose_explanation(drafts: list[Draft], avoid: frozenset = frozenset()) -> str:
    """Предложение 1: сильнейший уникальный атом + подтверждение другим фактом. Предложение 2: цифры + флаги."""
    def order(d: Draft):
        return -d.weight, GROUP_ORDER.index(d.group)

    lead = [d for d in drafts if d.group != "flag" and d.group not in avoid
            and (d.type == "contrast" or d.group not in ("budget", "duration"))]
    uniques = sorted((d for d in lead if d.unique), key=order)
    primary = uniques[0] if uniques else min(lead, key=order, default=None)
    used = {primary.group} | set(primary.topics) if primary else set()
    confirm = next((d for d in sorted(lead, key=order) if d.group not in used and not d.topics & used), None)
    if confirm:
        used.add(confirm.group)
    first = "; ".join(d.text for d in (primary, confirm) if d)
    numbers = [d.text for d in drafts if d.group in ("budget", "duration") and d.group not in used]
    numbers += [d.text for d in drafts if d.group == "flag"]
    return " ".join(_cap(s) + "." for s in (first, "; ".join(numbers)) if s)


def lead_groups(drafts: list[Draft], text: str) -> frozenset:
    """Какие факты попали в предложение 1 (для повторной сборки без них)."""
    first = text.split(". ")[0].lower()
    return frozenset(d.group for d in drafts if d.group != "flag" and d.text.lower() in first)


def check_explanation(text: str, description: str) -> list[str]:
    """Пусто = объяснение прошло проверки DoD."""
    problems = []
    low = normalize(text)
    if any(normalize(p) in low for p in STOP_PHRASES):
        problems.append("stop_phrase")
    quotes = re.findall(r"«([^»]*)»", text)
    if not re.search(r"\d", text) and not quotes:
        problems.append("no_number_or_quote")
    if any(q.strip("…") not in description for q in quotes):
        problems.append("quote_not_in_description")
    return problems


def card_badges(c: Contractor, req: SearchRequest) -> list[str]:
    badges = [b for b in ("synthetic", "price_imputed", "city_imputed") if getattr(c, b)]
    if c.price_from_kzt == req.budget_kzt:
        badges.append("price_equals_budget")
    return badges


def explain_cards(top: list[tuple[Contractor, ScoreBreakdown]], req: SearchRequest,
                  ctx: ScoreContext, tr: Tr) -> list[Card]:
    shown = [c for c, _ in top]
    drafts = {c.id: build_atoms(c, req, ctx, tr) for c in shown}
    _apply_contrasts(shown, drafts, req, ctx, tr)
    items_by_id, texts = {}, {}
    for c in shown:
        items = list(drafts[c.id].values())
        text = compose_explanation(items)
        if check_explanation(text, c.description):  # цитата с мусором → без цитаты
            items = [d for d in items if d.group != "quote"]
            text = compose_explanation(items)
        items_by_id[c.id], texts[c.id] = items, text
    names = tuple(c.name for c in shown)
    for i, j in itertools.combinations(range(len(shown)), 2):  # страховка DoD: тексты без имён не путаются
        a, b = shown[i], shown[j]
        if are_interchangeable(texts[a.id], texts[b.id], names):
            retry = compose_explanation(items_by_id[b.id], avoid=lead_groups(items_by_id[b.id], texts[b.id]))
            if not are_interchangeable(texts[a.id], retry, names) and not check_explanation(retry, b.description):
                texts[b.id] = retry
    cards = []
    for c, breakdown in top:
        atoms = sorted((d.atom() for d in items_by_id[c.id]), key=lambda a: (-a.unique, -a.weight))
        cards.append(Card(id=c.id, name=c.name, category=req.category, city=c.city,
                          price_from_kzt=c.price_from_kzt, badges=card_badges(c, req), explanation=texts[c.id],
                          atoms=atoms, score=breakdown.total, score_breakdown=dict(breakdown.parts)))
    return cards


def _signature(text: str, names: tuple[str, ...]) -> list[str]:
    t = normalize(text)
    for name in names:
        t = t.replace(normalize(name), " ")
    t = re.sub(r"\d[\d\s.,]*", " # ", t)
    return re.findall(r"#|[0-9a-zа-я]+", t)


def are_interchangeable(a: str, b: str, names: tuple[str, ...] = ()) -> bool:
    """True, если без имён и чисел тексты совпадают или почти совпадают по словам (Жаккар ≥ 0.8)."""
    sa, sb = _signature(a, names), _signature(b, names)
    if sa == sb:
        return True
    A, B = set(sa), set(sb)
    return len(A & B) / max(1, len(A | B)) >= 0.8


# ---------- «почему не больше» ----------

def _with_also(r: Rejection, tr: Tr) -> str:
    extra = [tr(f"why.short.{x}") for x in r.reasons[1:]]
    return f"{r.name} ({tr('why.also', list=', '.join(extra))})" if extra else r.name


def why_not_more(catalog, req: SearchRequest, rejected: list[Rejection],
                 lower: list[Contractor], tr: Tr) -> list[dict]:
    """Отсеянные — группами по первичной причине; отдельно «ещё N подходят, но ниже в рейтинге»."""
    lang, order = req.lang, {c.id: i for i, c in enumerate(catalog.contractors)}
    groups: dict[str, list[Rejection]] = {}
    for r in rejected:
        if r.reasons:
            groups.setdefault(r.reasons[0], []).append(r)
    lines = []
    for reason in REASON_ORDER:
        items = sorted(groups.get(reason, []), key=lambda r: (len(r.reasons) > 1,
                       catalog.by_id[r.id].price_from_kzt, order.get(r.id, 0)))
        if not items:
            continue
        names = [_with_also(r, tr) for r in items]
        form = "many" if len(items) > 1 else "one"
        if reason == "busy":
            text = tr(f"why.busy.{form}", names=", ".join(names), date=fmt_date(req.date, tr))
        elif reason == "format":
            text = tr(f"why.format.{form}", names=", ".join(names), format=tr(f"data.format_pl.{req.event_type}"))
        elif reason == "budget":
            parts = [tr("why.budget_item", name=n, price=fmt_kzt(catalog.by_id[r.id].price_from_kzt, lang))
                     for r, n in zip(items, names)]
            text = tr("why.budget", items=", ".join(parts), budget=fmt_kzt(req.budget_kzt, lang))
        elif reason == "language":
            text = tr(f"why.language.{form}", names=", ".join(names), language=tr(f"data.language_prep.{req.language}"))
        else:
            parts = [tr("why.duration_item", name=n, max=catalog.by_id[r.id].max_hours) for r, n in zip(items, names)]
            text = tr("why.duration", items=", ".join(parts), dur=req.duration_h)
        lines.append({"reason": reason, "ids": [r.id for r in items], "text": text})
    if lower:
        names = [c.name for c in lower]
        listed = ", ".join(names[:5]) + (", …" if len(names) > 5 else "")
        lines.append({"reason": "rank", "ids": [c.id for c in lower],
                      "text": tr("why.more", n=len(lower), verb=plural(tr("why.more_verb"), len(lower), lang),
                                 names=listed)})
    return lines


# ---------- совместимость с фазой 4 (summary, воронка, «почему не больше» v1 в engine/pages) ----------

Translator = Tr
badges_for = card_badges


def has_stop_phrase(text: str) -> bool:
    low = text.lower().replace("ё", "е")
    return any(p in low for p in STOP_PHRASES)


def label(tr: Tr, kind: str, value: Optional[str]) -> str:
    if not value:
        return ""
    key = f"data.{kind}.{value}"
    text = tr(key)
    return value if text == key else text


def join_human(items, tr: Tr) -> str:
    return fmt_list(list(items), tr)


def format_plural(value: str, tr: Tr) -> str:
    key = f"explain.format_pl.{value}"
    text = tr(key)
    return label(tr, "format", value) if text == key else text
