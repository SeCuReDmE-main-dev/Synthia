import json
from pathlib import Path

from synthia_core.cli import main
from synthia_core.nss_articles import NSSArticleIndex, NSSMathIndexScorer
from synthia_core.safety import HIERARCHY


FIXTURE_HTML = """
<html><body>
<a href="https://fs.unm.edu/NSS/NSS-98-2026.pdf">Neutrosophic Sets and Systems, Vol. 98, 2026</a>
<a href="https://fs.unm.edu/NSS/1PlithogenicContradiction.pdf">Plithogenic contradiction degree and attribute values</a>
<a href="1PlithogenicContradiction.pdf">Plithogenic contradiction degree and attribute values duplicate</a>
<a href="2NeutrosophicTopology.pdf">Advancing Neutrosophic &pi; Topology through closed sets</a>
<a href="3ProbabilityDistribution.pdf">Neutrosophic probability distribution and random variable entropy</a>
<a href="4SymbolicAlgebra.pdf">Symbolic plithogenic algebraic structure</a>
<a href="5Hypersoft.pdf">Hypersoft multi-criteria taxonomy filtering</a>
</body></html>
"""


def test_nss_article_parser_normalizes_deduplicates_and_marks_records():
    records = NSSArticleIndex().parse_html(FIXTURE_HTML)

    assert len(records) == 6
    assert records[0].record_type == "volume_pdf"
    assert records[1].record_type == "article_pdf"
    assert records[1].url == "https://fs.unm.edu/NSS/1PlithogenicContradiction.pdf"
    assert records[2].url == "https://fs.unm.edu/NSS/2NeutrosophicTopology.pdf"
    assert "?" in records[2].title_ascii
    assert records[1].selected_family == "plithogenic"


def test_nss_math_index_scorer_routes_core_math_families():
    scorer = NSSMathIndexScorer()

    probability = scorer.score_text("neutrosophic probability distribution random variable entropy")
    plithogenic = scorer.score_text("plithogenic contradiction dominant value attribute")
    topology = scorer.score_text("neutrosophic topology closed set metric space")
    hypersoft = scorer.score_text("hypersoft soft set parameter multi-criteria classification")
    symbolic = scorer.score_text("symbolic plithogenic algebraic structure")

    assert probability.selected_family == "probability_statistics"
    assert plithogenic.selected_family == "plithogenic"
    assert topology.selected_family in {"topology", "neutrogeometry"}
    assert hypersoft.selected_family == "hypersoft"
    assert symbolic.selected_family == "symbolic_algebra"

    for distribution in [probability, plithogenic, topology, hypersoft, symbolic]:
        payload = distribution.as_dict()
        assert 0.0 <= payload["H_lex"] <= 1.0
        assert 0.0 <= payload["G_lex"] <= 1.0
        assert 0.0 <= payload["I_lexicon"] <= 1.0
        assert payload["hierarchy"] == HIERARCHY
        assert "D_f" not in json.dumps(payload)
        assert "i_fractal" not in json.dumps(payload)


def test_nss_article_cli_scan_classify_source_and_explain(tmp_path: Path, capsys):
    fixture = tmp_path / "Articles.htm"
    fixture.write_text(FIXTURE_HTML, encoding="utf-8")
    private_org = tmp_path / "Synthia_organisation"

    code = main(
        [
            "nss",
            "articles",
            "scan",
            "--limit",
            "4",
            "--html",
            str(fixture),
            "--private-org",
            str(private_org),
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["total_records"] == 4
    assert payload["public_output"] == "sanitized_scan_summary_only"
    ledger_path = Path(payload["ledger_path"])
    assert ledger_path.exists()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["records"][1]["selected_family"] == "plithogenic"
    assert "raw html" not in json.dumps(payload).lower()

    code = main(["nss", "articles", "classify", "--text", "plithogenic contradiction degree"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected_family"] == "plithogenic"
    assert payload["tif"]["I_lexicon"] is not None

    code = main(
        [
            "nss",
            "articles",
            "source",
            "--url",
            "PlithogenicSetAnExtensionOfCrisp.pdf",
            "--title",
            "Plithogenic set attribute contradiction",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["record"]["url"] == "https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf"
    assert payload["record"]["selected_family"] == "plithogenic"

    code = main(["nss", "index", "explain", "--text", "hypersoft multi-criteria taxonomy filtering"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected_family"] == "hypersoft"
    assert payload["hierarchy"] == HIERARCHY
