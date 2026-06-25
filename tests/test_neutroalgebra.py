import json

from synthia_core.cli import main
from synthia_core.neutroalgebra import (
    NEUTROALGEBRA_SOURCE_URL,
    classify_neutroalgebra_operation,
    evaluate_neutroalgebra_axiom,
)


def test_neutroalgebra_classifies_indeterminate_operation():
    payload = classify_neutroalgebra_operation({"carrier": ["a", "b"], "table": {"a,a": "a", "a,b": "I", "b,a": "b"}})

    assert payload["classification"] == "neutroalgebra_indeterminate_operation"
    assert payload["indeterminate_slots"] == 1
    assert payload["partial_slots"] == 1
    assert payload["source"]["url"] == NEUTROALGEBRA_SOURCE_URL


def test_neutroalgebra_axiom_diagnostics():
    table = {"carrier": ["a", "b"], "table": {"a,a": "a", "a,b": "b", "b,a": "a", "b,b": "b"}}
    commutativity = evaluate_neutroalgebra_axiom("commutativity", table)

    assert commutativity["status"] == "invalid"
    assert commutativity["failure_count"] > 0


def test_neutroalgebra_cli_smoke(capsys):
    assert main(["neutroalgebra", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == NEUTROALGEBRA_SOURCE_URL

    operation = '{"carrier":["a","b"],"table":{"a,a":"a","a,b":"I","b,a":"b"}}'
    assert main(["neutroalgebra", "classify", "--operation", operation]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["classification"] == "neutroalgebra_indeterminate_operation"

    table = '{"carrier":["a","b"],"table":{"a,a":"a","a,b":"b","b,a":"a","b,b":"b"}}'
    assert main(["neutroalgebra", "axiom", "--axiom", "commutativity", "--table", table]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "invalid"


def test_i_chain_includes_neutroalgebra_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "neutroalgebra partial algebra neutrooperation neutroaxiom", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["neutroalgebra_profile"]["classification"] == "neutroalgebra_indeterminate_operation"
