import json

from synthia_core.cli import main
from synthia_core.plithogenic_set import PLITHOGENIC_SET_SOURCE_URL, operate_plithogenic_sets, score_plithogenic_set


def test_plithogenic_set_contradiction_against_dominant_attribute():
    payload = score_plithogenic_set(
        [
            {"name": "color", "value": "green", "T": 0.9, "I": 0.1, "F": 0.0, "dominant": True},
            {"name": "color", "value": "brown", "T": 0.3, "I": 0.4, "F": 0.5},
        ]
    )

    assert payload["attribute_count"] == 2
    assert payload["dominant_attribute"]["value"] == "green"
    assert payload["contradiction_load"] > 0.0
    assert payload["operational_tif"]["I_system^S"] == payload["contradiction_load"]


def test_plithogenic_set_operations():
    union = operate_plithogenic_sets("union", {"T": 0.4, "I": 0.2, "F": 0.6}, {"T": 0.7, "I": 0.5, "F": 0.3})
    intersection = operate_plithogenic_sets("intersection", {"T": 0.4, "I": 0.2, "F": 0.6}, {"T": 0.7, "I": 0.5, "F": 0.3})
    complement = operate_plithogenic_sets("complement", {"T": 0.4, "I": 0.2, "F": 0.6})

    assert union["result"]["T"] == 0.7
    assert union["result"]["F"] == 0.3
    assert intersection["result"]["T"] == 0.4
    assert intersection["result"]["F"] == 0.6
    assert complement["result"]["T"] == 0.6
    assert complement["result"]["F"] == 0.4


def test_plithogenic_set_cli_smoke(capsys):
    assert main(["plithogenic", "set", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == PLITHOGENIC_SET_SOURCE_URL

    attributes = '[{"name":"color","value":"green","T":0.9,"I":0.1,"F":0.0,"dominant":true},{"name":"color","value":"brown","T":0.3,"I":0.4,"F":0.5}]'
    assert main(["plithogenic", "set", "score", "--attributes", attributes]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["attribute_count"] == 2

    assert main(["plithogenic", "set", "operate", "--op", "union", "--left", '{"T":0.4,"I":0.2,"F":0.6}', "--right", '{"T":0.7,"I":0.5,"F":0.3}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"]["T"] == 0.7


def test_i_chain_includes_plithogenic_set_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "plithogenic set dominant value attribute spectrum", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["plithogenic_set_profile"]["attribute_count"] == 2
