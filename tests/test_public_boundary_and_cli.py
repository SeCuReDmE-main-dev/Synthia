import json
from pathlib import Path

from synthia_core.cli import main
from synthia_core.safety import assert_public_path
from synthia_core.soul import build_public_soul_summary


def test_public_path_rejects_private_markers():
    try:
        assert_public_path("private_evidence/gmail_aguilar_evidence.json")
    except ValueError as exc:
        assert "private-looking" in str(exc)
    else:
        raise AssertionError("private path should be rejected")


def test_public_soul_summary_filters_private_evidence(tmp_path: Path):
    private_org = tmp_path / "Synthia_organisation"
    soul_dir = private_org / "01_soul_and_storyline"
    soul_dir.mkdir(parents=True)
    (soul_dir / "synthia_soul.md").write_text(
        "Public line\nRaw private correspondence stays in private_evidence.\n",
        encoding="utf-8",
    )

    summary = build_public_soul_summary(private_org)

    assert "Public line" in summary
    assert "private_evidence" not in summary


def test_public_nss_docs_keep_clean_chain():
    root = Path(__file__).resolve().parents[1]
    docs = [
        root / "docs" / "nss_math_sources_for_synthia.md",
        root / "docs" / "nss_hub_system_classification_doctrine.md",
        root / "docs" / "nss_articles_indexation_for_i_lexicon.md",
        root / "docs" / "neutrosophic_foundation_kernel.md",
        root / "docs" / "neutrosophic_set_membership_kernel.md",
        root / "docs" / "neutrosophic_logic_kernel.md",
        root / "docs" / "single_valued_neutrosophic_kernel.md",
        root / "docs" / "neutrosophic_probability_kernel.md",
        root / "docs" / "neutrosophic_statistics_distribution_kernel.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "I -> I_system^S -> H_lex -> G_lex -> I_lexicon" in text
        assert "private_evidence" not in text.lower()
        assert "token" not in text.lower()
        assert "unpublished" not in text.lower()


def test_cli_lexicon_classify_smoke(capsys):
    code = main(
        [
            "lexicon",
            "classify",
            "--text",
            "AI-assisted traceability supports human review.",
            "--domain",
            "ai_governance",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["matched_terms"][0]["term"] == "AI-assisted traceability"
    assert payload["i_lexicon_classification"]["plithogenic_classified_as"] == "I_system^S"


def test_cli_i_chain_and_notation_smoke(capsys):
    code = main(["lexicon", "i-chain", "explain", "--term", "plithogenic contradiction"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected_layer"] == "I_lexicon"
    assert payload["carrier_type"] == "lexicon_distribution"

    code = main(["lexicon", "notation", "render", "--symbol", "I_s", "--format", "algorithm"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["symbol"] == "I_system^S"
    assert "system_scope" in payload["rendered"]


def test_cli_plithogenic_profile_smoke(capsys):
    code = main(["plithogenic", "profile", "--source", "nss.plithogenic_logic"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["canonical_indeterminacy_class"] == "I_system^S"
    assert payload["requested_source"]["url"] == "https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf"
    assert "raw_gmail_body" not in json.dumps(payload).lower()


def test_cli_nss_sources_and_route_smoke(capsys):
    code = main(["nss", "sources", "list"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["entrydoor"] == "https://fs.unm.edu/NSS/"
    assert payload["hierarchy"] == "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"

    code = main(["nss", "route", "--text", "plithogenic contradiction degree"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected_family"]["family_id"] == "plithogenic"
    assert payload["carrier_type"] == "lexicon_distribution"
    assert payload["plithogenic_profile"]["canonical_indeterminacy_class"] == "I_system^S"


def test_cli_taxonomy_packet_smoke(capsys):
    code = main(["taxonomy", "aburria-packet"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["formal_name"] == "Aburria aburri"
