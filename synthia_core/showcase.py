"""Public, reviewable showcase traces derived from Synthia memory records.

The showcase layer is intentionally separate from private evidence stores.  It
exports only curated public metadata and keeps nomenclatural decisions under
human authority.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


SHOWCASE_SCHEMA_VERSION = "synthia.showcase.trace.v1"
PUBLIC_HIERARCHY = "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"
SUPPORTED_CASES = ("aburria",)

_PRIVATE_MARKERS = (
    "client_secret",
    "gmail",
    "gdoc.",
    "drive.google.com",
    "private_evidence",
    "auth.json",
    "password",
    "refresh_token",
    "access_token",
    "c:\\users\\",
)
_OUT_OF_SCOPE_FIELDS = frozenset({"D_f", "dF", "i_fractal"})


def build_aburria_showcase_trace() -> dict[str, Any]:
    """Build the curated public trace for the *Aburria aburri* case.

    This is a candidate memory repair, not a nomenclatural act.  The source
    registry therefore records public evidence and leaves interpretation to a
    qualified human reviewer.
    """

    trace: dict[str, Any] = {
        "schema_version": SHOWCASE_SCHEMA_VERSION,
        "case_id": "aburria-aburri-memory-repair",
        "canonical_taxon": "Aburria aburri",
        "formal_authority": "Lesson, 1828",
        "review_status": "candidate_memory_for_human_review",
        "timeline": [
            {
                "event_id": "original-authority",
                "year": 1828,
                "event_type": "formal_authority",
                "citation": "Lesson, 1828",
                "public_url": None,
                "summary_key": "timeline.original",
            },
            {
                "event_id": "critical-redescription",
                "year": 2012,
                "event_type": "redescription",
                "citation": (
                    "H. F. Aguilar & R. F. Aguilar H. (2012). "
                    "Redescripción del gualí, Aburria aburri (Lesson, 1828) "
                    "(Craciformes: Cracidae), con notas sobre el nido y el huevo. "
                    "Revista de Ecología Latinoamericana 17(3):53-61."
                ),
                "public_url": None,
                "summary_key": "timeline.redescription",
            },
            {
                "event_id": "modern-taxonomy-context",
                "year": 2026,
                "event_type": "taxonomic_context",
                "citation": (
                    "Taxonomy of Aburria Reichenbach, 1853 (Aves, Galliformes, "
                    "Cracidae) based on morphological characters. Papéis Avulsos "
                    "de Zoologia 66:e202566014."
                ),
                "public_url": "https://doi.org/10.11606/1807-0205/2026.66.014",
                "summary_key": "timeline.modern",
            },
        ],
        "memory_repairs": [
            "morphology",
            "ecology",
            "nesting",
            "diagnostic_context",
        ],
        "unresolved_layers": [
            "source_interpretation",
            "taxonomic_context",
        ],
        "source_registry": [
            {
                "source_id": "aguilar-aguilar-2012-redescription",
                "year": 2012,
                "kind": "critical_redescription",
                "citation": (
                    "Aguilar, H. F. & Aguilar H., R. F. (2012), Revista de "
                    "Ecología Latinoamericana 17(3):53-61."
                ),
                "public_url": None,
            },
            {
                "source_id": "paz-2026-aburria-taxonomy",
                "year": 2026,
                "kind": "peer_reviewed_taxonomic_context",
                "citation": "Papéis Avulsos de Zoologia 66:e202566014.",
                "public_url": "https://revistas.usp.br/paz/article/view/237191",
            },
            {
                "source_id": "ncbi-taxonomy-aburria-aburri",
                "year": 2026,
                "kind": "current_registry_context",
                "citation": "NCBI Taxonomy Browser: Aburria aburri (Taxonomy ID 125058).",
                "public_url": (
                    "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/"
                    "wwwtax.cgi?id=125058&mode=info"
                ),
            },
        ],
        "authority_boundary": (
            "Candidate memory for human review; formal nomenclatural authority "
            "remains human and Code-governed."
        ),
        "human_review_required": True,
        "ai_role": "traceability_support_only",
        "hierarchy": PUBLIC_HIERARCHY,
        "locales": {
            "en": {
                "language": "English",
                "eyebrow": "Living Taxonomy",
                "title": "See a scientific memory repair itself",
                "subtitle": (
                    "Synthia turns scattered public evidence into a traceable "
                    "candidate memory without replacing expert judgment."
                ),
                "repairs_title": "Memory layers restored",
                "unresolved_title": "Still unresolved",
                "sources_title": "Public source registry",
                "boundary_title": "Authority boundary",
                "timeline.original": "The formal authority remains Lesson, 1828.",
                "timeline.redescription": (
                    "A 2012 redescription restores morphology, ecology, nesting, "
                    "and diagnostic context to the candidate memory."
                ),
                "timeline.modern": (
                    "A 2026 peer-reviewed treatment supplies current taxonomic context."
                ),
            },
            "fr": {
                "language": "Français",
                "eyebrow": "Taxonomie vivante",
                "title": "Voir une mémoire scientifique se réparer",
                "subtitle": (
                    "Synthia transforme des preuves publiques dispersées en mémoire "
                    "candidate traçable, sans remplacer le jugement expert."
                ),
                "repairs_title": "Couches de mémoire restaurées",
                "unresolved_title": "Encore non résolu",
                "sources_title": "Registre des sources publiques",
                "boundary_title": "Limite d’autorité",
                "timeline.original": "L’autorité formelle demeure Lesson, 1828.",
                "timeline.redescription": (
                    "Une redescription de 2012 restaure la morphologie, l’écologie, "
                    "la nidification et le contexte diagnostique."
                ),
                "timeline.modern": (
                    "Un traitement évalué par les pairs en 2026 apporte le contexte "
                    "taxonomique actuel."
                ),
            },
            "es": {
                "language": "Español",
                "eyebrow": "Taxonomía viva",
                "title": "Observa cómo se repara una memoria científica",
                "subtitle": (
                    "Synthia convierte evidencia pública dispersa en una memoria "
                    "candidata trazable sin sustituir el juicio experto."
                ),
                "repairs_title": "Capas de memoria restauradas",
                "unresolved_title": "Aún sin resolver",
                "sources_title": "Registro de fuentes públicas",
                "boundary_title": "Límite de autoridad",
                "timeline.original": "La autoridad formal sigue siendo Lesson, 1828.",
                "timeline.redescription": (
                    "Una redescripción de 2012 restaura morfología, ecología, "
                    "nidificación y contexto diagnóstico."
                ),
                "timeline.modern": (
                    "Un estudio revisado por pares de 2026 aporta contexto taxonómico actual."
                ),
            },
            "it": {
                "language": "Italiano",
                "eyebrow": "Tassonomia vivente",
                "title": "Guarda una memoria scientifica ripararsi",
                "subtitle": (
                    "Synthia trasforma prove pubbliche disperse in una memoria candidata "
                    "tracciabile senza sostituire il giudizio esperto."
                ),
                "repairs_title": "Strati di memoria ripristinati",
                "unresolved_title": "Ancora irrisolto",
                "sources_title": "Registro delle fonti pubbliche",
                "boundary_title": "Confine di autorità",
                "timeline.original": "L’autorità formale resta Lesson, 1828.",
                "timeline.redescription": (
                    "Una ridescrizione del 2012 ripristina morfologia, ecologia, "
                    "nidificazione e contesto diagnostico."
                ),
                "timeline.modern": (
                    "Uno studio peer-reviewed del 2026 fornisce il contesto tassonomico attuale."
                ),
            },
        },
    }
    assert_public_showcase_trace(trace)
    return trace


def build_showcase_trace(case_id: str) -> dict[str, Any]:
    """Build one of the explicitly supported public showcase cases."""

    if case_id == "aburria":
        return build_aburria_showcase_trace()
    supported = ", ".join(SUPPORTED_CASES)
    raise ValueError(f"unsupported showcase case {case_id!r}; choose one of: {supported}")


def assert_public_showcase_trace(trace: Mapping[str, Any]) -> None:
    """Fail closed if a showcase trace exposes private or out-of-scope data."""

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if key in _OUT_OF_SCOPE_FIELDS:
                    raise ValueError(f"out-of-scope field in showcase trace: {key}")
                lowered_key = str(key).lower()
                if any(marker in lowered_key for marker in _PRIVATE_MARKERS):
                    raise ValueError(f"private marker in showcase field: {key}")
                walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child)
        elif isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in _PRIVATE_MARKERS):
                raise ValueError("private marker in showcase value")

    walk(trace)
    if trace.get("schema_version") != SHOWCASE_SCHEMA_VERSION:
        raise ValueError("invalid showcase schema version")
    if trace.get("hierarchy") != PUBLIC_HIERARCHY:
        raise ValueError("public Synthia hierarchy was changed")
    if trace.get("human_review_required") is not True:
        raise ValueError("showcase traces must require human review")
    if trace.get("ai_role") != "traceability_support_only":
        raise ValueError("AI role must remain traceability support only")


def write_showcase_trace(case_id: str, output: str | Path, *, pretty: bool = False) -> Path:
    """Write a deterministic, public-safe showcase trace to ``output``."""

    trace = build_showcase_trace(case_id)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        trace,
        ensure_ascii=False,
        indent=2 if pretty else None,
        sort_keys=True,
    )
    destination.write_text(serialized + "\n", encoding="utf-8")
    return destination
