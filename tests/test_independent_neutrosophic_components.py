import json

from synthia_core.cli import main
from synthia_core.independent_neutrosophic_components import COMPONENTS_SOURCE_URL, classify_components


def test_components_classify_modes_and_offsets():
    independent = classify_components(0.7, 0.2, 0.1, "independent")
    dependent = classify_components(0.7, 0.2, 0.1, "dependent")
    offset = classify_components(1.2, 0.2, -0.1, "offset")

    assert independent["primary_classification"] == "independent_components"
    assert independent["dependency_score"] == 0.0
    assert dependent["dependency_score"] == 1.0
    assert dependent["operational_tif"]["I_system^S"] == 1.0
    assert "offset_components" in offset["component_classification"]
    assert offset["operational_tif"]["T"] == 1.0
    assert offset["operational_tif"]["F"] == 0.0


def test_components_cli_smoke(capsys):
    assert main(["nss", "components", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == COMPONENTS_SOURCE_URL

    assert main(["nss", "components", "classify", "--T", "1.2", "--I", "0.2", "--F", "-0.1", "--mode", "offset"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["primary_classification"] == "offset_components"


def test_i_chain_includes_independent_components_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "independent component trivariate truth", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["independent_components_profile"]["primary_classification"] == "independent_components"
