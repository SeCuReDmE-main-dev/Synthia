import json

from synthia_core.cli import main
from synthia_core.plithogenic_logic import PLITHOGENIC_LOGIC_SOURCE_URL, classify_plithogenic_logic


def test_plithogenic_logic_cumulative_truth_and_categories():
    payload = classify_plithogenic_logic(
        [
            {"name": "V1", "T": 0.8, "I": 0.1, "F": 0.1, "dependence": 0.2},
            {"name": "V2", "T": 0.6, "I": 0.3, "F": 0.2, "dependence": 0.4},
        ]
    )

    assert payload["variable_count"] == 2
    assert payload["cumulative_truth"]["T"] == 0.7
    assert payload["dependence_load"] == 0.30000000000000004
    assert "plithogenic_neutrosophic_logic" in payload["logic_categories"]
    assert payload["operational_tif"]["I_system^S"] == 0.30000000000000004


def test_plithogenic_logic_cli_smoke(capsys):
    assert main(["plithogenic", "logic", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == PLITHOGENIC_LOGIC_SOURCE_URL

    variables = '[{"name":"V1","T":0.8,"I":0.1,"F":0.1},{"name":"V2","T":0.6,"I":0.3,"F":0.2}]'
    assert main(["plithogenic", "logic", "classify", "--variables", variables]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["variable_count"] == 2


def test_i_chain_includes_plithogenic_logic_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "plithogenic logic cumulative truth proposition", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["plithogenic_logic_profile"]["variable_count"] == 2
