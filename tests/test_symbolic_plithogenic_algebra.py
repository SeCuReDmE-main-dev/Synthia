import json

from synthia_core.cli import main
from synthia_core.symbolic_plithogenic_algebra import (
    SYMBOLIC_PLITHOGENIC_SOURCE_URL,
    SymbolicPlithogenicNumber,
    operate_symbolic_plithogenic_numbers,
)


def test_symbolic_number_parses_and_normalizes_coefficients():
    payload = SymbolicPlithogenicNumber.from_raw({"base": 2, "components": {"P1": 0.5, "P2": 0.25}}).as_dict()

    assert payload["base"] == 2.0
    assert payload["coefficients"]["P1"] == 0.5
    assert payload["expression"] == "2.0 + 0.5P1 + 0.25P2"
    assert payload["source"]["url"] == SYMBOLIC_PLITHOGENIC_SOURCE_URL


def test_symbolic_add_and_subtract():
    add = operate_symbolic_plithogenic_numbers(
        "add",
        {"base": 1, "components": {"P1": 0.5}},
        {"base": 2, "components": {"P1": 0.25, "P2": 0.1}},
    )
    subtract = operate_symbolic_plithogenic_numbers(
        "subtract",
        {"base": 1, "components": {"P1": 0.5}},
        {"base": 2, "components": {"P1": 0.25}},
    )

    assert add["result"]["base"] == 3.0
    assert add["result"]["coefficients"]["P1"] == 0.75
    assert subtract["result"]["base"] == -1.0
    assert subtract["result"]["coefficients"]["P1"] == 0.25


def test_symbolic_cli_smoke(capsys):
    assert main(["symbolic-plithogenic", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == SYMBOLIC_PLITHOGENIC_SOURCE_URL

    assert main(["symbolic-plithogenic", "number", "parse", "--value", '{"base":1,"components":{"P1":0.5}}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["coefficients"]["P1"] == 0.5

    assert main(["symbolic-plithogenic", "operate", "--op", "add", "--left", '{"base":1,"components":{"P1":0.5}}', "--right", '{"base":2,"components":{"P1":0.25}}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"]["base"] == 3.0


def test_i_chain_includes_symbolic_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "symbolic plithogenic algebraic structure", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["symbolic_plithogenic_profile"]["coefficients"]["P1"] == 0.4
