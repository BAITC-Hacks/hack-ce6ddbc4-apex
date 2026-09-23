"""Факты из описания: стаж, объём, масштаб, языки, форматы — у каждого точный фрагмент-основание.

Жёсткие фильтры работают только по полям CSV. Описание даёт факты «по описанию», и каждый
хранит исходный фрагмент (evidence_spans): объяснение можно проверить глазами.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

CURRENT_YEAR = 2026  # год календаря данных: «с 2015 года» → 11 лет

# Казахские буквы → близкие русские, ё → е. Длина строки не меняется, индексы совпадают с оригиналом.
_FOLD = str.maketrans({"ё": "е", "ә": "а", "ғ": "г", "қ": "к", "ң": "н", "ө": "о",
                       "ұ": "у", "ү": "у", "һ": "х", "і": "и"})


def normalize(text: str) -> str:
    out = []
    for ch in text or "":
        low = ch.lower()
        out.append(low if len(low) == 1 else ch)
    return "".join(out).translate(_FOLD)


# Числа словами. Основа (родительный падеж = первая часть сложного слова) работает и в
# «около семи лет», и в «шестилетней», «десятилетний». Именительный — «пять лет», «два года».
NUM_STEMS = {
    "одного": 1, "одно": 1, "двух": 2, "трех": 3, "четырех": 4, "пяти": 5, "шести": 6, "семи": 7,
    "восьми": 8, "девяти": 9, "десяти": 10, "одиннадцати": 11, "двенадцати": 12, "тринадцати": 13,
    "четырнадцати": 14, "пятнадцати": 15, "шестнадцати": 16, "семнадцати": 17, "восемнадцати": 18,
    "девятнадцати": 19, "двадцати": 20,
}
NUM_WORDS = {
    "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8,
    "девять": 9, "десять": 10, "одиннадцать": 11, "двенадцать": 12, "тринадцать": 13,
    "четырнадцать": 14, "пятнадцать": 15, "шестнадцать": 16, "семнадцать": 17,
    "восемнадцать": 18, "девятнадцать": 19, "двадцать": 20, **NUM_STEMS,
}


def _alt(words) -> str:
    return "|".join(sorted(words, key=len, reverse=True))  # длинные первыми: «пятнадцати» раньше «пяти»


PLUS = r"(?P<plus>более\s+(?:чем\s+)?|свыше\s+|больше\s+)?"
NUM = r"(?<![\d.,])(?P<num>\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)"
YEARS_PATTERNS = (
    re.compile(PLUS + r"(?<![\d.,])(?P<num>\d{1,2})\s*(?P<p2>\+)?\s*(?:лет|года|год)\b"),  # 13 лет, более 12 лет
    re.compile(PLUS + r"(?<![\d.,])(?P<num>\d{1,2})\s*-?\s*летн\w*"),                      # 10-летним опытом
    re.compile(PLUS + r"(?:около\s+)?\b(?P<word>" + _alt(NUM_WORDS) + r")\s+(?:лет|года|год)\b"),  # около семи лет
    re.compile(r"\b(?P<stem>" + _alt(NUM_STEMS) + r")летн\w*"),                             # шестилетней
    re.compile(r"\bс\s+(?P<year>(?:19|20)\d{2})\s*(?:года|г\.)"),                           # с 2015 года
)
EXPERIENCE_CUE = re.compile(r"опыт|стаж|работ|веду|вед[её]т|уже|более|свыше|около|истори|на\s+рынке|"
                            r"\bза\b|професси|занима|снима|созда|провел|провож|\bс\s+(?:19|20)\d\d")
NOT_EXPERIENCE = re.compile(r"(?:\bот|\bдо|юбиле\w*|возраст\w*|детям|исполн\w*)\s*$")
EVENTS_RE = re.compile(
    PLUS + NUM + r"\s*(?P<p2>\+)?\s*(?:(?!(?:лет|года|год|тенге|тг|руб\w*|долл\w*)\b)[а-яa-z-]+\s+){0,2}?"
    r"(?P<noun>свад\w*|мероприяти\w*|ивент\w*|событи\w*|съем\w*|заказ\w*|проект\w*|праздник\w*|торжеств\w*)"
)
NOUN_KIND = (("свад", "wedding"), ("мероприят", "event"), ("ивент", "event"), ("событ", "event"),
             ("съем", "shoot"), ("заказ", "order"), ("проект", "project"), ("праздник", "celebration"),
             ("торжеств", "celebration"))
PER_MONTH = re.compile(r"ежемесячн|в\s+месяц|каждый\s+месяц")
AUDIENCE_RE = re.compile(NUM + r"\s*(?P<p2>\+)?\s*(?:человек\w*|чел\b\.?|гост\w*|участник\w*|зрител\w*|персон\w*)")
LANGUAGE_PATTERNS = (  # значения — как в CSV
    ("казахский", re.compile(r"казахск\w*|казакш\w*|\bказ\b|\bказак\b")),
    ("русский", re.compile(r"русск\w*|\bрус\b|орысш\w*")),
    ("английский", re.compile(r"английск\w*|\bангл\b|english|агылшын\w*")),
)
FORMAT_PATTERNS = (  # традиционные и деловые форматы, названные в тексте
    ("kyz_uzatu", re.compile(r"проводы\s+невест\w*|кыз\s+узат\w*")),
    ("tusaukeser", re.compile(r"обряд\w*\s+первых\s+шагов|тусау\s*-?\s*кесер\w*")),
    ("betashar", re.compile(r"беташар\w*")),
    ("teambuilding", re.compile(r"тимбилдинг\w*|team\s*-?\s*building")),
    ("forum", re.compile(r"форум\w*")),
    ("conference", re.compile(r"конференц\w*")),
)


@dataclass(frozen=True)
class Facts:
    years_min: Optional[int] = None
    events_count: Optional[int] = None
    events_noun: Optional[str] = None               # wedding|event|shoot|order|project|celebration
    audience_max: Optional[int] = None
    languages_mentioned: tuple[str, ...] = ()
    formats_mentioned: tuple[str, ...] = ()         # kyz_uzatu|tusaukeser|betashar|teambuilding|forum|conference
    evidence_spans: tuple[tuple[str, str], ...] = ()  # (факт, точный фрагмент описания)
    years_plus: bool = False                        # «более 12 лет» → в тексте «12+ лет»
    events_plus: bool = False
    events_period: Optional[str] = None             # "month": «ежемесячно … более 1000 заказов»

    def evidence(self, kind: str) -> Optional[str]:
        return next((text for k, text in self.evidence_spans if k == kind), None)

    @property
    def has_experience(self) -> bool:
        return self.years_min is not None or self.events_count is not None


def _sentence(norm: str, pos: int) -> str:
    start = max(norm.rfind(ch, 0, pos) for ch in ".!?•\n") + 1
    ends = [i for i in (norm.find(ch, pos) for ch in ".!?•\n") if i != -1]
    return norm[start:min(ends) if ends else len(norm)]


def _int(value: str) -> int:
    return int(re.sub(r"\D", "", value))


def _years(text: str, norm: str) -> Optional[tuple[int, bool, str]]:
    best = None
    for pattern in YEARS_PATTERNS:
        for m in pattern.finditer(norm):
            g = m.groupdict()
            if g.get("year"):
                value = CURRENT_YEAR - int(g["year"])
            elif g.get("num"):
                value = _int(g["num"])
            else:
                value = NUM_WORDS.get(g.get("word") or "") or NUM_STEMS.get(g.get("stem") or "")
            if not value or not 1 <= value <= 50:
                continue
            if not EXPERIENCE_CUE.search(_sentence(norm, m.start())):
                continue
            if NOT_EXPERIENCE.search(norm[max(0, m.start() - 16):m.start()]):
                continue
            candidate = (value, bool(g.get("plus") or g.get("p2")), text[m.start():m.end()].strip())
            if best is None or candidate[0] > best[0]:
                best = candidate
    return best


def _events(text: str, norm: str) -> Optional[tuple[int, bool, str, str, Optional[str]]]:
    best = None
    for m in EVENTS_RE.finditer(norm):
        value = _int(m.group("num"))
        if not 10 <= value <= 100_000:  # «0 разводов», «топ-3», цены — не объём работ
            continue
        kind = next(k for prefix, k in NOUN_KIND if m.group("noun").startswith(prefix))
        period = "month" if PER_MONTH.search(_sentence(norm, m.start())) else None
        candidate = (value, bool(m.group("plus") or m.group("p2")), kind, text[m.start():m.end()].strip(), period)
        if best is None or candidate[0] > best[0]:
            best = candidate
    return best


@lru_cache(maxsize=512)
def extract_facts(description: str) -> Facts:
    text = description or ""
    norm = normalize(text)
    spans: list[tuple[str, str]] = []
    years = _years(text, norm)
    if years:
        spans.append(("years", years[2]))
    events = _events(text, norm)
    if events:
        spans.append(("events", events[3]))
    audience = None
    for m in AUDIENCE_RE.finditer(norm):
        value = _int(m.group("num"))
        if value >= 10 and (audience is None or value > audience[0]):
            audience = (value, text[m.start():m.end()].strip())
    if audience:
        spans.append(("audience", audience[1]))
    languages, formats = [], []
    for value, pattern in LANGUAGE_PATTERNS:
        m = pattern.search(norm)
        if m:
            languages.append(value)
            spans.append((f"language:{value}", text[m.start():m.end()]))
    for code, pattern in FORMAT_PATTERNS:
        m = pattern.search(norm)
        if m:
            formats.append(code)
            spans.append((f"format:{code}", text[m.start():m.end()]))
    return Facts(
        years_min=years[0] if years else None,
        years_plus=years[1] if years else False,
        events_count=events[0] if events else None,
        events_plus=events[1] if events else False,
        events_noun=events[2] if events else None,
        events_period=events[4] if events else None,
        audience_max=audience[0] if audience else None,
        languages_mentioned=tuple(languages),
        formats_mentioned=tuple(formats),
        evidence_spans=tuple(spans),
    )
