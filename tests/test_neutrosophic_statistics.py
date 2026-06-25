import json

from synthia_core.cli import main
from synthia_core.neutrosophic_statistics import (
    DISTRIBUTION_SOURCE_URL,
    STATISTICS_SOURCE_URL,
    classify_neutrosophic_distribution,
    summarize_neutrosophic_dataset,
)


def test_statistics_summary_known_interval_unknown():
    payload = summarize_neutrosophic_dataset([1, 2, [3, 5], None, {"unknown": True}])

    assert payload["dataset_size"] == 5
    assert payload["known_count"] == 2
    assert payload["interval_count"] == 1
    assert payload["unknown_count"] == 2
    assert payload["indeterminacy_load"] == 0.6
    assert payload["review_risk"] == "medium"
    assert payload["range"] == {"min": 1.0, "max": 4.0}


def test_distribution_classification_labels():
    payload = classify_neutrosophic_distribution("binomial trial with success failure and indeterminate interval")

    assert payload["primary_distribution"] == "neutrosophic_binomial_candidate"
    assert "indeterminate_distribution" in payload["candidate_distribution_labels"]
    assert payload["source"]["url"] == DISTRIBUTION_SOURCE_URL


def test_statistics_cli_smoke(capsys):
    assert main(["nss", "statistics", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["sources"][0]["url"] == STATISTICS_SOURCE_URL

    assert main(["nss", "statistics", "summarize", "--values", '[1,2,[3,5],null,{"unknown":true}]']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["unknown_count"] == 2

    assert main(["nss", "distribution", "classify", "--text", "normal distribution with unknown interval"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "neutrosophic_normal_candidate" in payload["candidate_distribution_labels"]
