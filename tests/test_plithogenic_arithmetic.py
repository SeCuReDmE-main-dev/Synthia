import json

from synthia_core.cli import main
from synthia_core.plithogenic_arithmetic import (
    PLITHOGENIC_ARITHMETIC_SOURCE_URL,
    multiply_symbolic_plithogenic_numbers,
)


def test_plithogenic_multiply_uses_absorbance_law():
    payload = multiply_symbolic_plithogenic_numbers(
        {"base": 1, "components": {"P1": 0.5}},
        {"base": 2, "components": {"P1": 0.25, "P2": 0.1}},
    )

    assert payload["source"]["url"] == PLITHOGENIC_ARITHMETIC_SOURCE_URL
    assert payload["result"]["base"] == 2.0
    assert payload["result"]["coefficients"]["P1"] == 1.375
    assert payload["result"]["coefficients"]["P2"] == 0.1
    assert payload["result"]["coefficients"]["P1*P2"] == 0.05


def test_plithogenic_multiply_cli_smoke(capsys):
    assert main(["symbolic-plithogenic", "multiply", "--left", '{"base":1,"components":{"P1":0.5}}', "--right", '{"base":2,"components":{"P1":0.25}}']) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "multiply"
    assert payload["law"]["name"] == "absorbance"


def test_i_chain_includes_plithogenic_arithmetic_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "plithogenic arithmetic multiplication absorbance", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["plithogenic_arithmetic_profile"]["operation"] == "multiply"
