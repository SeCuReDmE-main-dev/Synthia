import json

from synthia_core.cli import main
from synthia_core.plithogenic_probability_statistics import (
    PLITHOGENIC_PROBABILITY_SOURCE_URL,
    refine_plithogenic_probability,
    summarize_plithogenic_probability_event,
)
from synthia_core.safety import HIERARCHY


def test_plithogenic_probability_event_refines_variables_and_projects_i_lexicon():
    payload = summarize_plithogenic_probability_event(
        [
            {"name": "A", "T": 0.8, "I": 0.1, "F": 0.1, "weight": 2},
            {"name": "B", "T": 0.2, "I": 0.6, "F": 0.5, "weight": 1},
        ]
    )

    assert payload["variable_count"] == 2
    assert payload["refined_components"][0]["variable"] == "A"
    assert payload["contradiction_load"] > 0
    assert payload["operational_tif"]["I_system^S"] == payload["operational_tif"]["I_lexicon"]
    assert payload["hierarchy"] == HIERARCHY


def test_plithogenic_probability_refine_preserves_public_source():
    payload = refine_plithogenic_probability([{"name": "C", "T": 1.2, "I": 0.4, "F": -0.2}])

    assert payload["source"]["url"] == PLITHOGENIC_PROBABILITY_SOURCE_URL
    assert payload["variables"][0]["formal_value"]["T"] == 1.2
    assert payload["variables"][0]["operational_tif"]["T"] == 1.0


def test_plithogenic_probability_cli_smoke(capsys):
    assert main(["plithogenic", "probability", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == PLITHOGENIC_PROBABILITY_SOURCE_URL

    variables = '[{"name":"A","T":0.8,"I":0.1,"F":0.1},{"name":"B","T":0.2,"I":0.6,"F":0.5}]'
    assert main(["plithogenic", "probability", "event", "--variables", variables]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["variable_count"] == 2

    assert main(["plithogenic", "probability", "refine", "--components", variables]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["refinement_rule"]


def test_i_chain_includes_plithogenic_probability_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "plithogenic probability statistics refined components", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["plithogenic_probability_profile"]["variable_count"] == 2
