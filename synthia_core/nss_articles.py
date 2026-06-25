"""NSS article-index parsing and I_lexicon math scoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from math import log
from pathlib import Path
from re import sub
from typing import Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


NSS_ARTICLES_URL = "https://fs.unm.edu/NSS/Articles.htm"
NSS_BASE_URL = "https://fs.unm.edu/NSS/"


FAMILY_KEYWORDS: dict[str, tuple[tuple[str, float], ...]] = {
    "TIF": (
        ("truth", 1.2),
        ("indeterminacy", 1.4),
        ("falsity", 1.2),
        ("single valued", 1.0),
        ("neutrosophic set", 1.0),
    ),
    "probability_statistics": (
        ("probability", 1.6),
        ("statistics", 1.5),
        ("statistical", 1.4),
        ("distribution", 1.5),
        ("random variable", 1.7),
        ("expected value", 1.2),
        ("variance", 1.1),
        ("standard deviation", 1.0),
        ("cdf", 0.9),
        ("pdf", 0.9),
        ("entropy", 1.2),
        ("measure", 0.9),
    ),
    "independent_components": (
        ("independent component", 1.8),
        ("independent neutrosophic", 1.7),
        ("offset component", 1.7),
        ("trivariate", 1.2),
        ("multivariate truth", 1.2),
    ),
    "multineutrosophic": (
        ("multineutrosophic", 2.0),
        ("multi neutrosophic", 2.0),
        ("multi-source", 1.4),
        ("many sources", 1.2),
        ("source fusion", 1.2),
    ),
    "plithogenic": (
        ("plithogenic", 2.0),
        ("contradiction", 1.7),
        ("dominant value", 1.5),
        ("cumulative truth", 1.5),
        ("attribute spectrum", 1.3),
        ("attribute", 1.0),
        ("multi-attribute", 1.3),
        ("multivariate", 1.1),
    ),
    "symbolic_algebra": (
        ("symbolic", 1.7),
        ("algebra", 1.2),
        ("algebraic", 1.2),
        ("number", 0.7),
        ("structure", 0.8),
    ),
    "hypersoft": (
        ("hypersoft", 2.0),
        ("soft set", 1.5),
        ("parameter", 0.9),
        ("multi-criteria", 1.1),
        ("rough fuzzy", 0.8),
    ),
    "neutroalgebra": (
        ("neutroalgebra", 2.0),
        ("partial algebra", 1.7),
        ("operation", 0.9),
        ("axiom", 1.0),
        ("subalgebra", 1.0),
    ),
    "neutrogeometry": (
        ("neutrogeometry", 2.0),
        ("geometry", 1.0),
        ("metric space", 1.3),
        ("normed space", 1.1),
        ("fractal", 1.5),
        ("dimension", 0.8),
    ),
    "topology": (
        ("topology", 1.8),
        ("topological", 1.7),
        ("closed set", 1.3),
        ("open set", 1.1),
        ("separation", 1.0),
        ("continuous", 0.8),
    ),
    "decision_making": (
        ("decision making", 1.6),
        ("decision-making", 1.6),
        ("madm", 1.4),
        ("mcdm", 1.4),
        ("topsis", 1.2),
        ("ahp", 1.0),
        ("vikor", 1.0),
        ("optimization", 0.8),
    ),
    "graph_theory": (
        ("graph", 1.6),
        ("network", 1.0),
        ("vertex", 1.0),
        ("edge", 1.0),
        ("hypergraph", 1.5),
    ),
    "physics": (
        ("physics", 1.4),
        ("quantum", 1.5),
        ("mechanics", 1.0),
        ("electromagnetic", 1.1),
        ("nanofluid", 1.0),
        ("thermal", 0.8),
    ),
    "future_math_lexicon": (
        ("extension", 0.7),
        ("generalized", 0.6),
        ("new", 0.4),
        ("model", 0.4),
    ),
}


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._href: str | None = None
        self._parts: list[str] = []
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = {key.lower(): value for key, value in attrs}
        self._href = attributes.get("href")
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._href is not None:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._href is not None:
            self._parts.append(f"&#{name};")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._href is None:
            return
        label = normalize_title(" ".join(self._parts))
        self.anchors.append((self._href, label))
        self._href = None
        self._parts = []


def normalize_title(title: str) -> str:
    cleaned = unescape(title)
    cleaned = sub(r"<[^>]+>", " ", cleaned)
    cleaned = sub(r"\s+", " ", cleaned).strip()
    return cleaned


def ascii_fallback(text: str) -> str:
    return text.encode("ascii", "replace").decode("ascii")


def _decode_html(raw: bytes) -> str:
    for encoding in ("utf-8", "windows-1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_nss_articles_html(url: str = NSS_ARTICLES_URL, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "Synthia-NSS-Indexer/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return _decode_html(response.read())


def _source_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    stem = Path(parsed.path).stem.lower()
    stem = sub(r"[^a-z0-9]+", "_", stem).strip("_") or "article"
    return f"nss.article.{stem}"


def _is_pdf_url(url: str) -> bool:
    return ".pdf" in urlparse(url).path.lower()


def _is_volume_pdf(url: str, title: str) -> bool:
    name = Path(urlparse(url).path).name.lower()
    lowered = title.lower()
    return name.startswith("nss-") or "neutrosophic sets and systems, vol." in lowered


@dataclass(frozen=True)
class NSSArticleFamilyScore:
    family_id: str
    score: float
    probability: float
    matched_keywords: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "score": self.score,
            "probability": self.probability,
            "matched_keywords": list(self.matched_keywords),
        }


@dataclass(frozen=True)
class NSSLexiconDistribution:
    text: str
    family_scores: tuple[NSSArticleFamilyScore, ...]
    H_lex: float
    G_lex: float
    I_lexicon: float
    selected_family: str
    contradiction_load: float

    @property
    def selected_probability(self) -> float:
        if not self.family_scores:
            return 0.0
        return self.family_scores[0].probability

    def tif(self) -> TIF:
        return TIF(
            T=self.selected_probability,
            I=self.I_lexicon,
            F=clamp01(1.0 - self.selected_probability),
            I_system=self.I_lexicon,
            H_lex=self.H_lex,
            G_lex=self.G_lex,
            I_lexicon=self.I_lexicon,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "selected_family": self.selected_family,
            "selected_probability": self.selected_probability,
            "family_scores": [score.as_dict() for score in self.family_scores],
            "P(L_i | d, S)": {
                score.family_id: score.probability for score in self.family_scores
            },
            "H_lex": self.H_lex,
            "G_lex": self.G_lex,
            "I_lexicon": self.I_lexicon,
            "contradiction_load": self.contradiction_load,
            "tif": self.tif().as_dict(),
            "hierarchy": HIERARCHY,
            "boundary": "Article-index classification is a candidate routing signal, not final scholarly authority.",
        }


@dataclass(frozen=True)
class NSSArticleRecord:
    source_id: str
    title: str
    url: str
    title_ascii: str
    record_type: str
    selected_family: str
    family_scores: tuple[NSSArticleFamilyScore, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "title_ascii": self.title_ascii,
            "url": self.url,
            "record_type": self.record_type,
            "selected_family": self.selected_family,
            "family_scores": [score.as_dict() for score in self.family_scores],
        }


@dataclass(frozen=True)
class NSSIndexScanResult:
    source_url: str
    scanned_at: str
    total_records: int
    records: tuple[NSSArticleRecord, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "source_url": self.source_url,
            "scanned_at": self.scanned_at,
            "total_records": self.total_records,
            "records": [record.as_dict() for record in self.records],
            "hierarchy": HIERARCHY,
            "public_boundary": "Generated ledgers belong in Synthia_organisation, not the public repo.",
        }


class NSSMathIndexScorer:
    """Deterministic keyword-weight scorer for NSS math article titles."""

    def __init__(self, family_keywords: dict[str, tuple[tuple[str, float], ...]] | None = None) -> None:
        self.family_keywords = family_keywords or FAMILY_KEYWORDS

    def score_text(self, text: str) -> NSSLexiconDistribution:
        lowered = text.lower()
        raw_scores: dict[str, float] = {}
        matched: dict[str, list[str]] = {}
        for family_id, keywords in self.family_keywords.items():
            total = 0.0
            hits: list[str] = []
            for keyword, weight in keywords:
                if keyword in lowered:
                    total += weight
                    hits.append(keyword)
            if total > 0.0:
                raw_scores[family_id] = total
                matched[family_id] = hits

        if not raw_scores:
            raw_scores = {"future_math_lexicon": 1.0}
            matched = {"future_math_lexicon": []}

        score_sum = sum(raw_scores.values()) or 1.0
        probabilities = {
            family_id: raw_score / score_sum for family_id, raw_score in raw_scores.items()
        }
        ordered = sorted(probabilities.items(), key=lambda item: (-item[1], item[0]))
        family_scores = tuple(
            NSSArticleFamilyScore(
                family_id=family_id,
                score=raw_scores[family_id],
                probability=clamp01(probability),
                matched_keywords=tuple(matched.get(family_id, ())),
            )
            for family_id, probability in ordered
        )
        h_lex = self._entropy(probabilities.values())
        top = ordered[0][1]
        second = ordered[1][1] if len(ordered) > 1 else 0.0
        g_lex = clamp01(1.0 - max(0.0, top - second))
        contradiction_load = self._contradiction_load(lowered, top, second)
        i_lexicon = clamp01(0.45 * h_lex + 0.35 * g_lex + 0.20 * contradiction_load)
        return NSSLexiconDistribution(
            text=text,
            family_scores=family_scores,
            H_lex=h_lex,
            G_lex=g_lex,
            I_lexicon=i_lexicon,
            selected_family=family_scores[0].family_id,
            contradiction_load=contradiction_load,
        )

    @staticmethod
    def _entropy(probabilities: Iterable[float]) -> float:
        values = [value for value in probabilities if value > 0.0]
        if len(values) <= 1:
            return 0.0
        entropy = -sum(value * log(value) for value in values)
        return clamp01(entropy / log(len(values)))

    @staticmethod
    def _contradiction_load(text: str, top: float, second: float) -> float:
        explicit = 0.35 if any(word in text for word in ("contradiction", "conflict", "inconsistent")) else 0.0
        close_decision = 0.25 if second > 0.0 and abs(top - second) <= 0.10 else 0.0
        return clamp01(max(explicit, close_decision))


class NSSArticleIndex:
    """Parser and scanner for the public NSS Articles.htm index."""

    def __init__(self, scorer: NSSMathIndexScorer | None = None) -> None:
        self.scorer = scorer or NSSMathIndexScorer()

    def parse_html(self, html: str, limit: int | None = None) -> tuple[NSSArticleRecord, ...]:
        parser = _AnchorParser()
        parser.feed(html)
        seen: set[str] = set()
        records: list[NSSArticleRecord] = []
        for href, label in parser.anchors:
            absolute_url = urljoin(NSS_BASE_URL, href)
            if not _is_pdf_url(absolute_url) or absolute_url in seen:
                continue
            seen.add(absolute_url)
            title = label or Path(urlparse(absolute_url).path).stem
            distribution = self.scorer.score_text(title)
            records.append(
                NSSArticleRecord(
                    source_id=_source_id_from_url(absolute_url),
                    title=title,
                    url=absolute_url,
                    title_ascii=ascii_fallback(title),
                    record_type="volume_pdf" if _is_volume_pdf(absolute_url, title) else "article_pdf",
                    selected_family=distribution.selected_family,
                    family_scores=distribution.family_scores,
                )
            )
            if limit is not None and len(records) >= limit:
                break
        return tuple(records)

    def scan(self, limit: int | None = None, html: str | None = None, source_url: str = NSS_ARTICLES_URL) -> NSSIndexScanResult:
        source_html = html if html is not None else fetch_nss_articles_html(source_url)
        records = self.parse_html(source_html, limit=limit)
        return NSSIndexScanResult(
            source_url=source_url,
            scanned_at=datetime.now(timezone.utc).isoformat(),
            total_records=len(records),
            records=records,
        )

    def classify_text(self, text: str) -> dict[str, object]:
        payload = self.scorer.score_text(text).as_dict()
        payload["source_index"] = NSS_ARTICLES_URL
        return payload

    def classify_source(self, url: str, title: str | None = None) -> dict[str, object]:
        absolute_url = urljoin(NSS_BASE_URL, url)
        source_title = title or Path(urlparse(absolute_url).path).stem
        distribution = self.scorer.score_text(source_title)
        record = NSSArticleRecord(
            source_id=_source_id_from_url(absolute_url),
            title=source_title,
            title_ascii=ascii_fallback(source_title),
            url=absolute_url,
            record_type="volume_pdf" if _is_volume_pdf(absolute_url, source_title) else "article_pdf",
            selected_family=distribution.selected_family,
            family_scores=distribution.family_scores,
        )
        return {
            "record": record.as_dict(),
            "distribution": distribution.as_dict(),
            "source_index": NSS_ARTICLES_URL,
        }
