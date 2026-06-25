import json

from synthia_core.cli import main
from synthia_core.single_valued_neutrosophic import SVNS_SOURCE_URL, SingleValuedNeutrosophicSet, SVNSOperator


def test_svns_union_intersection_difference():
    operator = SVNSOperator()
    left = SingleValuedNeutrosophicSet(0.4, 0.2, 0.6, label="left")
    right = SingleValuedNeutrosophicSet(0.7, 0.5, 0.3, label="right")

    union = operator.operate("union", left, right)["result"]
    intersection = operator.operate("intersection", left, right)["result"]
    difference = operator.operate("difference", left, right)["result"]

    assert union["T"] == 0.7
    assert union["I"] == 0.5
    assert union["F"] == 0.3
    assert intersection["T"] == 0.4
    assert intersection["I"] == 0.2
    assert intersection["F"] == 0.6
    assert difference["T"] == 0.3
    assert difference["I"] == 0.2
    assert difference["F"] == 0.7


def test_svns_favorites_are_bounded():
    operator = SVNSOperator()
    value = SingleValuedNeutrosophicSet(0.8, 0.5, 0.7)

    truth = operator.favorite("truth", value)["result"]
    falsity = operator.favorite("falsity", value)["result"]

    assert truth["T"] == 1.0
    assert truth["I"] == 0.0
    assert truth["F"] == 0.7
    assert falsity["T"] == 0.8
    assert falsity["I"] == 0.0
    assert falsity["F"] == 1.0


def test_svns_cli_smoke(capsys):
    assert main(["nss", "svns", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == SVNS_SOURCE_URL

    assert main(["nss", "svns", "operate", "--op", "union", "--left", "0.4,0.2,0.6", "--right", "0.7,0.5,0.3"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"]["T"] == 0.7

    assert main(["nss", "svns", "favorite", "--mode", "truth", "--T", "0.8", "--I", "0.5", "--F", "0.7"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"]["T"] == 1.0
