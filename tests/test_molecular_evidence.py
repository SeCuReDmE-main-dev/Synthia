import json

from synthia_core.cli import main
from synthia_core.molecular_evidence import (
    ENSEMBL_GUARDRAIL_SOURCE_ID,
    NCBI_BLAST_GUARDRAIL_SOURCE_ID,
    NCBI_DATASETS_GUARDRAIL_SOURCE_ID,
    NSS_DNA_SEQUENCE_SOURCE_ID,
    MolecularReviewCase,
    MolecularReviewPriority,
    build_dna_similarity_demo_case,
    score_molecular_review_case,
)
from synthia_core.safety import HIERARCHY


def test_parser_preserves_source_ids_formal_metrics_and_bounds():
    case = MolecularReviewCase.from_raw_case(
        {
            "case_label": "Parser molecular case",
            "query_label": "Synthetic query",
            "source_ids": ["source.case"],
            "evidence_records": [
                {
                    "id": "record.a",
                    "provider": "ncbi_blast",
                    "molecule_type": "dna",
                    "label": "Record A",
                    "accession": "ACC001",
                    "taxon_label": "Synthetic taxon",
                    "taxon_id": "123",
                    "T": 1.2,
                    "I": 0.4,
                    "F": -0.1,
                    "weight": -3,
                    "source_ids": ["source.record"],
                    "percent_identity": 104.0,
                    "query_coverage": -10.0,
                    "evalue": 1e-20,
                    "bit_score": 1200.0,
                    "taxon_match": True,
                }
            ],
        }
    )
    payload = score_molecular_review_case(case)

    record = payload["evidence_records"][0]
    assert payload["source_ids"][:2] == ["source.case", "source.record"]
    assert record["formal_value"]["T"] == 1.2
    assert record["formal_metrics"]["percent_identity"] == 104.0
    assert record["formal_metrics"]["evalue"] == 1e-20
    assert record["operational_tif"]["T"] == 1.0
    assert record["operational_tif"]["F"] == 0.0
    assert record["operational_metrics"]["percent_identity"] == 1.0
    assert record["operational_metrics"]["query_coverage"] == 0.0
    assert record["operational_metrics"]["bit_score"] == 1.0
    assert record["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_empty_evidence_is_critical_and_bounded():
    payload = score_molecular_review_case({"case_label": "Empty molecular case", "evidence_records": []})

    assert payload["sequence_evidence_count"] == 0
    assert payload["dominant_evidence_record"] is None
    assert payload["molecular_support_signal"] == 0.0
    assert payload["contradiction_load"] == 1.0
    assert payload["uncertainty_load"] == 1.0
    assert payload["review_priority"] == MolecularReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0
    assert payload["operational_tif"]["F"] == 0.0


def test_high_molecular_disagreement_produces_review_priority():
    payload = score_molecular_review_case(
        {
            "case_label": "Contradicted molecular case",
            "query_label": "Synthetic query",
            "evidence_records": [
                {
                    "id": "record.conflicted",
                    "provider": "ncbi_blast",
                    "molecule_type": "marker_gene",
                    "label": "Conflicted record",
                    "accession": "ACC002",
                    "taxon_label": "Synthetic taxon",
                    "taxon_id": "456",
                    "T": 0.92,
                    "I": 0.8,
                    "F": 0.7,
                    "percent_identity": 99.0,
                    "query_coverage": 98.0,
                    "bit_score": 900.0,
                    "taxon_match": True,
                }
            ],
        }
    )

    assert payload["contradiction_load"] >= 0.75
    assert payload["review_priority"] == MolecularReviewPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["G_lex"] == payload["contradiction_load"]


def test_related_phase_payloads_are_preserved_without_authority_expansion():
    related_taxon = {"taxon_label": "Synthetic taxon", "human_review_required": True}
    related_risk = {"case_label": "Synthetic risk", "human_review_required": True}
    related_graph = {"graph_label": "Synthetic graph", "human_review_required": True}
    payload = score_molecular_review_case(
        {
            "case_label": "Linked molecular case",
            "related_taxon_packet": related_taxon,
            "related_risk_case": related_risk,
            "related_biology_graph": related_graph,
            "evidence_records": [
                {
                    "id": "record.linked",
                    "provider": "ensembl",
                    "molecule_type": "genome_region",
                    "label": "Linked annotation",
                    "T": 0.7,
                    "I": 0.2,
                    "F": 0.1,
                    "annotation_match": True,
                }
            ],
        }
    )

    assert payload["related_taxon_packet"] == related_taxon
    assert payload["related_risk_case"] == related_risk
    assert payload["related_biology_graph"] == related_graph
    assert "no formal taxonomic act" in payload["authority_boundary"]
    assert "autonomous molecular conclusion" in payload["authority_boundary"]


def test_demo_case_is_public_safe_and_guardrail_linked():
    payload = score_molecular_review_case(build_dna_similarity_demo_case())
    serialized = json.dumps(payload, ensure_ascii=False)

    assert payload["case_label"] == "Synthetic DNA similarity review case"
    assert payload["sequence_evidence_count"] == 3
    assert NSS_DNA_SEQUENCE_SOURCE_ID in payload["source_ids"]
    assert NCBI_BLAST_GUARDRAIL_SOURCE_ID in payload["source_ids"]
    assert NCBI_DATASETS_GUARDRAIL_SOURCE_ID in payload["source_ids"]
    assert ENSEMBL_GUARDRAIL_SOURCE_ID in payload["source_ids"]
    assert payload["source_anchor"]["url"] == "https://fs.unm.edu/NSS/27DNASequence.pdf"
    assert {source["source_id"] for source in payload["guardrail_sources"]} == {
        NCBI_BLAST_GUARDRAIL_SOURCE_ID,
        NCBI_DATASETS_GUARDRAIL_SOURCE_ID,
        ENSEMBL_GUARDRAIL_SOURCE_ID,
    }
    assert "ATGCATGCATGCATGCATGC" not in serialized
    assert "raw_alignment" not in serialized
    assert "private_thread_subject" not in serialized
    assert "raw_private_gmail_body" not in serialized
    assert "private_message_id" not in serialized


def test_cli_molecular_evidence_score_and_demo(capsys):
    case = {
        "case_label": "CLI molecular fixture",
        "query_label": "CLI query",
        "evidence_records": [
            {
                "id": "record.cli",
                "provider": "ncbi_datasets",
                "molecule_type": "dna",
                "label": "CLI record",
                "T": 0.68,
                "I": 0.22,
                "F": 0.1,
                "taxon_match": True,
            }
        ],
    }

    assert main(["molecular-evidence", "score", "--case", json.dumps(case)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["case_label"] == "CLI molecular fixture"
    assert payload["human_review_required"] is True

    assert main(["molecular-evidence", "demo"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_anchor"]["source_id"] == NSS_DNA_SEQUENCE_SOURCE_ID
