"""Цитаты-доказательства: ручной TF-IDF по символьным n-граммам 3–5 внутри слов (только stdlib).

n-граммы устойчивы к падежам («свадеб»/«свадьбы»), опечаткам и смеси RU/KZ, не требуют
словарей и моделей и полностью детерминированы.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Optional

from .facts import normalize
from .models import SearchRequest

NGRAM_MIN, NGRAM_MAX = 3, 5
MAX_QUOTE_WORDS = 12
WORD_RE = re.compile(r"[0-9a-zа-я]+")                  # по нормализованному тексту
SENT_END_RE = re.compile(r"[.!?]+(?=\s|$)|[•\n\r]+")   # . ! ? перед пробелом/концом, •, перевод строки
EDGE_PUNCT = " ,;:—–-()«»\"'“”"

FORMAT_SYNONYMS = {
    "свадьба": ("свадьб", "свадеб", "молодожен", "невест", "пар", "love story"),
    "той": ("той", "узату", "беташар", "казахск"),
    "корпоратив": ("корпоратив", "компан", "бизнес", "форум", "тимбилдинг"),
    "конференция": ("конференц", "форум", "спикер", "делов"),
    "юбилей": ("юбиле", "годовщин"),
    "день рождения": ("день рождения", "праздник", "детск"),
}
TRADITION_TERMS = ("проводы невесты", "обряд первых шагов", "тусаукесер", "кыз узату")  # + к свадьбе и тою
LANGUAGE_STEMS = {"русский": "русск", "казахский": "казахск", "английский": "английск"}


def ngrams(text: str) -> Counter:
    grams: Counter = Counter()
    for word in WORD_RE.findall(normalize(text)):
        for n in range(NGRAM_MIN, min(NGRAM_MAX, len(word)) + 1):
            for i in range(len(word) - n + 1):
                grams[word[i:i + n]] += 1
    return grams


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(g, 0.0) for g, v in a.items())


class TfidfIndex:
    """IDF по описаниям каталога; векторы L2-нормированы, поэтому скалярное произведение = косинус."""

    def __init__(self, docs: dict[str, str]):
        grams_by_doc = {doc_id: ngrams(text) for doc_id, text in docs.items()}
        df: Counter = Counter()
        for grams in grams_by_doc.values():
            df.update(grams.keys())
        n = len(docs)
        self.idf = {g: math.log((1 + n) / (1 + k)) + 1.0 for g, k in df.items()}
        self.default_idf = math.log(1 + n) + 1.0             # n-граммы, которых нет в каталоге
        self.doc_vectors = {doc_id: self.weigh(g) for doc_id, g in grams_by_doc.items()}

    def weigh(self, grams: Counter) -> dict[str, float]:
        vec = {g: (1.0 + math.log(tf)) * self.idf.get(g, self.default_idf) for g, tf in grams.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {g: v / norm for g, v in vec.items()}

    def vector(self, text: str) -> dict[str, float]:
        return self.weigh(ngrams(text))

    def similarity(self, doc_id: str, query_vec: dict[str, float]) -> float:
        return cosine(self.doc_vectors.get(doc_id, {}), query_vec)


_INDEX_CACHE: dict[int, TfidfIndex] = {}


def get_index(catalog) -> TfidfIndex:
    """Индекс строится один раз на каталог (~50 мс) и живёт в памяти процесса."""
    key = hash(tuple((c.id, c.description) for c in catalog.contractors))
    index = _INDEX_CACHE.get(key)
    if index is None:
        index = TfidfIndex({c.id: c.description for c in catalog.contractors})
        _INDEX_CACHE.clear()
        _INDEX_CACHE[key] = index
    return index


def build_query(req: SearchRequest) -> str:
    """Запрос = синонимы формата (+ традиции для свадьбы/тоя) + категория + язык + пожелания."""
    parts = list(FORMAT_SYNONYMS.get(req.event_type, (req.event_type,)))
    if req.event_type in ("свадьба", "той"):
        parts += TRADITION_TERMS
    parts.append(req.category)
    if req.language:
        parts.append(LANGUAGE_STEMS.get(req.language, req.language))
    if req.wishes:
        parts.append(req.wishes)
    return " ".join(parts)


def split_sentences(text: str) -> list[tuple[int, int]]:
    """Границы предложений в ИСХОДНОЙ строке — цитата всегда будет её точной подстрокой."""
    cuts, start = [], 0
    for m in SENT_END_RE.finditer(text):
        cuts.append((start, m.start()))
        start = m.end()
    cuts.append((start, len(text)))
    spans = []
    for a, b in cuts:
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            spans.append((a, b))
    return spans


def _caps_heavy(s: str) -> bool:
    letters = [ch for ch in s if ch.isalpha()]
    return bool(letters) and sum(ch.isupper() for ch in letters) / len(letters) > 0.6


def find_quote(description: str, query: str, index: Optional[TfidfIndex] = None, *,
               banned: tuple[str, ...] = (), exclude: tuple[str, ...] = (),
               max_words: int = MAX_QUOTE_WORDS) -> tuple[str, float]:
    """(цитата, score). Цитата — точная подстрока описания (плюс «…» по краям), ≤ max_words слов."""
    text = description or ""
    weigh = index.weigh if index else _plain_weigh
    qvec = weigh(ngrams(query))
    banned_n = tuple(normalize(p) for p in banned)
    exclude_n = tuple(normalize(x) for x in exclude if x)
    candidates = []
    for pos, (a, b) in enumerate(split_sentences(text)):
        words = [(a + m.start(), a + m.end()) for m in re.finditer(r"\S+", text[a:b])]
        norm = normalize(text[a:b])
        if len(words) < 3 or any(p in norm for p in banned_n) or any(x in norm for x in exclude_n):
            continue
        score = cosine(weigh(ngrams(text[a:b])), qvec)
        if _caps_heavy(text[a:b]):
            score *= 0.8                         # КАПСЛОК цитируем только если больше нечего
        candidates.append((-round(score, 6), pos, len(words), words))
    if not candidates:
        return "", 0.0
    neg_score, _, _, words = min(candidates)     # детерминированно: score ↓, позиция ↑, длина ↑
    k = min(max_words, len(words))
    weights = [sum(qvec.get(g, 0.0) for g in ngrams(text[s:e])) for s, e in words]
    best_i = max(range(len(words) - k + 1), key=lambda i: (round(sum(weights[i:i + k]), 6), -i))
    qa, qb = words[best_i][0], words[best_i + k - 1][1]
    while qa < qb and text[qa] in EDGE_PUNCT:
        qa += 1
    while qb > qa and text[qb - 1] in EDGE_PUNCT:
        qb -= 1
    prefix = "…" if best_i > 0 else ""
    suffix = "…" if best_i + k < len(words) else ""
    return prefix + text[qa:qb] + suffix, -neg_score


def best_quote(description: str, query: str, index: Optional[TfidfIndex] = None, **kwargs) -> str:
    return find_quote(description, query, index, **kwargs)[0]


def _plain_weigh(grams: Counter) -> dict[str, float]:   # без индекса: tf без idf
    vec = {g: 1.0 + math.log(tf) for g, tf in grams.items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {g: v / norm for g, v in vec.items()}


@lru_cache(maxsize=4)
def load_enriched(path: str) -> dict:
    """(опц.) data/enriched.json из scripts/enrich_llm.py. Нет файла — пустой словарь, ядро не страдает."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data.get("profiles", {}) if isinstance(data, dict) else {}
