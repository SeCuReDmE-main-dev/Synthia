import json

from synthia_core.cli import main
from synthia_core.neutrosophic_logic import LOGIC_GENERALIZES_IFL_URL, LogicCompatibilityClassifier
from synthia_core.safety import HIERARCHY


def test_logic_classifier_paradox_and_ifl_boundary():
    payload = LogicCompatibilityClassifier().classify(0.9, 0.2, 0.9, text="paradox proposition")

    assert payload["primary_classification"] == "relative_truth"
    assert "paraconsistent" in payload["logic_classification"]
    assert "paradoxist" in payload["logic_classification"]
    assert payload["ifl_compatibility"]["is_ifs_compatible"] is False
    assert payload["hierarchy"] == HIERARCHY


def test_logic_classifier_preserves_absolute_formal_values():
    payload = LogicCompatibilityClassifier().classify(1.2, 0.1, 1.1, text="absolute contradiction")

    assert "absolute_truth" in payload["logic_classification"]
    assert "absolute_falsity" in payload["logic_classification"]
    assert payload["formal_value"]["components"]["T"]["formal_value"] == 1.2
    assert payload["formal_value"]["components"]["F"]["formal_value"] == 1.1
    assert payload["operational_tif"]["T"] == 1.0
    assert payload["operational_tif"]["F"] == 1.0


def test_logic_cli_smoke(capsys):
    assert main(["nss", "logic", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["sources"][0]["url"] == LOGIC_GENERALIZES_IFL_URL
    assert "paraconsistent" in payload["classification_labels"]

    assert main(["nss", "logic", "classify", "--T", "0.2", "--I", "0.2", "--F", "0.2", "--text", "incomplete logic"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "incomplete" in payload["logic_classification"]

    assert main(["nss", "logic", "compare-ifl", "--T", "0.8", "--I", "0.1", "--F", "0.4"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["is_ifs_compatible"] is False


def test_i_chain_classify_includes_logic_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "paradox logic proposition", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["logic_profile"]["primary_classification"] == "relative_truth"
    assert "D_f" not in json.dumps(payload)
    assert "i_fractal" not in json.dumps(payload)
