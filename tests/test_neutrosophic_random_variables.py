import json

from synthia_core.cli import main
from synthia_core.neutrosophic_random_variables import (
    RANDOM_VARIABLE_SOURCE_URL,
    NeutrosophicRandomVariable,
    summarize_random_variables,
)
from synthia_core.safety import HIERARCHY


def test_random_variable_preserves_formal_value_and_projects_i_lexicon():
    payload = NeutrosophicRandomVariable("X", 2.0, 0.4).as_dict()

    assert payload["formal_value"]["base"] == 2.0
    assert payload["formal_value"]["I"] == 0.4
    assert payload["distribution_metadata"]["CDF"] == "F_XN(x) = F_X(x - I)"
    assert payload["expected_value"]["operational_expected_value"] == 2.4
    assert payload["i_lexicon_projection"]["I_lexicon"] == 0.4
    assert payload["hierarchy"] == HIERARCHY


def test_random_variable_summary_expected_variance_and_bounds():
    payload = summarize_random_variables([{"base": 1, "I": 0.2}, {"base": 3, "I": 0.4}])

    assert payload["count"] == 2
    assert payload["expected_value"] == 2.0
    assert payload["variance"] == 1.0
    assert payload["standard_deviation"] == 1.0
    assert payload["indeterminacy_load"] == 0.30000000000000004
    assert payload["operational_tif"]["I_lexicon"] == 0.30000000000000004


def test_random_variable_cli_smoke(capsys):
    assert main(["nss", "random-variable", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == RANDOM_VARIABLE_SOURCE_URL

    assert main(["nss", "random-variable", "define", "--name", "X", "--base", "2", "--I", "0.4"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "X"

    assert main(["nss", "random-variable", "summarize", "--values", '[{"base":1,"I":0.2},{"base":3,"I":0.4}]']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["expected_value"] == 2.0


def test_i_chain_includes_random_variable_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "random variable expected value and variance", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["random_variable_profile"]["name"] == "text_random_variable"
    assert "D_f" not in json.dumps(payload)
