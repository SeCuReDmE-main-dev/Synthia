import json

from synthia_core.cli import main
from synthia_core.plithogenic_hypersoft import (
    PLITHOGENIC_HYPERSOFT_SOURCE_URL,
    classify_hypersoft_mapping,
    hypersoft_product,
)


def test_hypersoft_product_builds_attribute_combinations():
    payload = hypersoft_product({"habitat": ["forest", "river"], "trait": ["leaf", "flower"]})

    assert payload["combination_count"] == 4
    assert payload["source"]["url"] == PLITHOGENIC_HYPERSOFT_SOURCE_URL


def test_plithogenic_hypersoft_classification_marks_unresolved_points():
    payload = classify_hypersoft_mapping(
        {
            "attributes": {"habitat": ["forest", "river"], "trait": ["leaf", "flower"]},
            "memberships": [{"point": {"habitat": "forest", "trait": "leaf"}, "T": 0.8, "I": 0.1, "F": 0.1}],
        }
    )

    assert payload["classification"] == "plithogenic_hypersoft"
    assert payload["unresolved_points"] == 3
    assert payload["operational_tif"]["I_lexicon"] > 0


def test_hypersoft_cli_smoke(capsys):
    assert main(["hypersoft", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == PLITHOGENIC_HYPERSOFT_SOURCE_URL

    assert main(["hypersoft", "product", "--attributes", '{"habitat":["forest","river"],"trait":["leaf","flower"]}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["combination_count"] == 4

    assert main(["hypersoft", "classify", "--mapping", '{"attributes":{"habitat":["forest"],"trait":["leaf"]},"memberships":[{"T":0.8,"I":0.1,"F":0.1}]}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["classification"] == "plithogenic_hypersoft"


def test_i_chain_includes_hypersoft_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "plithogenic hypersoft soft set attribute product", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["plithogenic_hypersoft_profile"]["classification"] == "plithogenic_hypersoft"
