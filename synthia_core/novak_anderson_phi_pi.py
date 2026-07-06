"""Novak-Anderson phi/pi governance case for Synthia.

This module keeps the theorem in Synthia's review and source-governance lane.
It does not duplicate the FNP-QNN simulator math engine and does not expose
private Gmail bodies, message ids, attachment ids, or display URLs.
"""

from __future__ import annotations

from .scientific_governance import (
    GovernanceEvidenceSource,
    GovernanceStandard,
    ScientificGovernanceCase,
    ValidationStatus,
)


ANDERSON_NOVAK_PHI_PI_SOURCE_ID = "ANDERSON_NOVAK_PHI_PI_2008"
ANDERSON_NOVAK_FIBONACCI_VECTOR_SOURCE_ID = "ANDERSON_NOVAK_FIBONACCI_VECTOR_POLYGONS_2009"
DANI_SHEET_SOURCE_ID = "DANI_NOVAK_PHI_HIGHER_DIMENSIONS_SHEET_REDACTED"
GENESIS_ECHOES_SOURCE_ID = "GENESIS_ECHOES_PAPER_I_DRIVE_DOC"
PRIVATE_GMAIL_PROVENANCE_SOURCE_ID = "PRIVATE_DANI_NOVAK_GMAIL_PROVENANCE_REDACTED"
LOCAL_FNP_QNN_RUNTIME_SOURCE_ID = "LOCAL_FNP_QNN_NOVAK_ANDERSON_RUNTIME"
PHI_FRAMEWORK_RESEARCH_SOURCE_ID = "PHI_FRAMEWORK_RESEARCH_DRIVE_DOC"
PHI_CALCULUS_CHEATSHEET_SOURCE_ID = "PHI_CALCULUS_CHEATSHEET_DRIVE_DOC"
BRIDGE_CALCULUS_SOURCE_ID = "BRIDGE_CALCULUS_DRIVE_DOC"
UNIFIED_FFED_CALCULI_SOURCE_ID = "UNIFIED_FFED_CALCULI_DRIVE_DOC"
ANTI_ENTROPY_IMPERATIVE_SOURCE_ID = "ANTI_ENTROPY_IMPERATIVE_DRIVE_DOC"

CLAIM_BOUNDARY = (
    "Synthia can govern source traceability for the implemented Novak-Anderson formulas and "
    "numeric convergence checks. It does not certify cosmology, cryptography, medicine, "
    "consciousness, production security, or autonomous scientific truth."
)


def build_novak_anderson_governance_case() -> ScientificGovernanceCase:
    """Build a public-safe governance case for the Novak-Anderson phi/pi layer."""

    evidence_sources = (
        GovernanceEvidenceSource(
            source_id=ANDERSON_NOVAK_PHI_PI_SOURCE_ID,
            standard=GovernanceStandard.PREDICTIVE_REPORTING.value,
            title="A Connection between the Numbers Phi and Pi",
            url=(
                "https://hascmathart.weebly.com/uploads/7/6/8/7/7687070/"
                "a_connection_between_the_numbers_phi_and_pi_2.pdf"
            ),
            coverage_T=0.92,
            coverage_I=0.06,
            coverage_F=0.02,
            weight=1.5,
            notes="Primary public source for pseudopi, inverse pseudopi, and pseudophi formulas.",
        ),
        GovernanceEvidenceSource(
            source_id=ANDERSON_NOVAK_FIBONACCI_VECTOR_SOURCE_ID,
            standard=GovernanceStandard.FAIR_DATA.value,
            title="Fibonacci Vector Sequences and Regular Polygons",
            url=(
                "https://www.researchgate.net/profile/Stuart-Anderson-2/publication/228768410_"
                "Fibonacci_vector_sequences_and_regular_polygons/links/54b5ec8c0cf26833efd345f7/"
                "Fibonacci-vector-sequences-and-regular-polygons.pdf"
            ),
            coverage_T=0.88,
            coverage_I=0.08,
            coverage_F=0.03,
            weight=1.4,
            notes="Primary public source for Fibonacci-vector recurrence and Golden Numbers.",
        ),
        GovernanceEvidenceSource(
            source_id=DANI_SHEET_SOURCE_ID,
            standard=GovernanceStandard.DATASET_SHEET.value,
            title="Phi in Higher Dimensions",
            url="https://docs.google.com/spreadsheets/d/1LICbMOdp689MwMvwToTQJkKf0SQNVKMNoRMKeRP1WFw/edit",
            coverage_T=0.74,
            coverage_I=0.20,
            coverage_F=0.04,
            weight=1.0,
            notes="Redacted private-provenance teaching Sheet; no private email body or message id is stored.",
        ),
        GovernanceEvidenceSource(
            source_id=GENESIS_ECHOES_SOURCE_ID,
            standard=GovernanceStandard.MODEL_CARD.value,
            title="Genesis Echoes, Paper I",
            url="https://docs.google.com/document/d/1kDqt3WML2ev0uBNH9OKseIb7XF5k6H9ScRzusJ47gf4/edit",
            coverage_T=0.46,
            coverage_I=0.48,
            coverage_F=0.16,
            weight=0.8,
            notes="Interpretive Phi Framework bridge; not primary mathematical proof.",
        ),
        GovernanceEvidenceSource(
            source_id=PHI_FRAMEWORK_RESEARCH_SOURCE_ID,
            standard=GovernanceStandard.MODEL_CARD.value,
            title="Phi Framework Research and Development",
            url="https://docs.google.com/document/d/10DNzmxVqZCvMNBN4tIvQpbkXwCLIIqbCnsx5TJlqj7s/edit",
            coverage_T=0.42,
            coverage_I=0.52,
            coverage_F=0.12,
            weight=0.5,
            notes="Deferred interpretive Phi Framework source; not primary theorem proof.",
        ),
        GovernanceEvidenceSource(
            source_id=PHI_CALCULUS_CHEATSHEET_SOURCE_ID,
            standard=GovernanceStandard.DATASET_SHEET.value,
            title="Phi Calculus Cheatsheet Development",
            url="https://docs.google.com/document/d/1sOi-vZhIZiyyOMPnu55S7eAuEKdI3lB8K4D5Z6zqJPw/edit",
            coverage_T=0.38,
            coverage_I=0.56,
            coverage_F=0.14,
            weight=0.5,
            notes="Deferred phi calculus source for future framework expansion.",
        ),
        GovernanceEvidenceSource(
            source_id=BRIDGE_CALCULUS_SOURCE_ID,
            standard=GovernanceStandard.DATASET_SHEET.value,
            title="Bridge Calculus: Elemental Transmutation",
            url="https://docs.google.com/document/d/14hBgjKn8QTjZjQUx0s8DuCNM7h12Q7zVQcgFM2MjA7Q/edit",
            coverage_T=0.34,
            coverage_I=0.60,
            coverage_F=0.16,
            weight=0.4,
            notes="Deferred bridge/elemental calculus source; not implemented in theorem-first module.",
        ),
        GovernanceEvidenceSource(
            source_id=UNIFIED_FFED_CALCULI_SOURCE_ID,
            standard=GovernanceStandard.AI_RISK_MANAGEMENT.value,
            title="A Unified Framework of FfeD Calculi",
            url="https://docs.google.com/document/d/1lH3OTdklWpRcT4QxZEPguzFsq1fwqUpG527W7emCY2g/edit",
            coverage_T=0.34,
            coverage_I=0.60,
            coverage_F=0.16,
            weight=0.4,
            notes="Deferred Air/Fire/Water/Earth/Bridge calculus source.",
        ),
        GovernanceEvidenceSource(
            source_id=ANTI_ENTROPY_IMPERATIVE_SOURCE_ID,
            standard=GovernanceStandard.AI_RISK_MANAGEMENT.value,
            title="The Anti-Entropy Imperative",
            url="https://docs.google.com/document/d/11f4kORbVcy3OmIRbQ00nxS76sPdw4V3orc0jffI7tA0/edit",
            coverage_T=0.30,
            coverage_I=0.64,
            coverage_F=0.18,
            weight=0.4,
            notes="Deferred anti-entropy source; no anti-entropy theorem implementation in this pass.",
        ),
        GovernanceEvidenceSource(
            source_id=PRIVATE_GMAIL_PROVENANCE_SOURCE_ID,
            standard=GovernanceStandard.AI_RISK_MANAGEMENT.value,
            title="Private Dani Novak provenance thread, redacted",
            url="[private Gmail provenance redacted]",
            coverage_T=0.50,
            coverage_I=0.44,
            coverage_F=0.06,
            weight=0.7,
            notes="Confirms provenance route only; no Gmail body, message id, attachment id, or display URL is stored.",
        ),
    )
    source_ids = tuple(source.source_id for source in evidence_sources) + (LOCAL_FNP_QNN_RUNTIME_SOURCE_ID,)
    return ScientificGovernanceCase(
        case_label="Novak-Anderson phi/pi theorem governance case",
        review_subject="FNP-QNN Novak-Anderson phi/pi theorem convergence module",
        intended_use="Education, source traceability, formula verification, and human-review preparation.",
        out_of_scope_use=(
            "Scientific certification beyond the cited formulas, physics validation, cryptographic assurance, "
            "clinical use, consciousness claims, production security, or autonomous conclusion."
        ),
        evidence_sources=evidence_sources,
        validation_status=ValidationStatus.SOURCE_LINKED.value,
        source_ids=source_ids,
        reviewer_notes=CLAIM_BOUNDARY,
        related_algorithm_behavior={
            "case_label": "FNP-QNN Novak-Anderson runtime behavior boundary",
            "deterministic": True,
            "uses_stim_for_proof": False,
            "human_review_required": True,
            "claim_boundary": CLAIM_BOUNDARY,
        },
    )


def score_novak_anderson_governance_case() -> dict[str, object]:
    """Return the scored governance payload for CLI and tests."""

    from .scientific_governance import score_scientific_governance_case

    return score_scientific_governance_case(build_novak_anderson_governance_case())
