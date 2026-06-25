import json

from synthia_core.cli import main
from synthia_core.neutrosophic_probability import (
    PROBABILITY_SOURCE_URL,
    NeutrosophicEvent,
    NeutrosophicProbability,
    NeutrosophicSampleSpace,
)
from synthia_core.safety import HIERARCHY


def test_probability_event_and_complement():
    event = NeutrosophicEvent("rain", NeutrosophicProbability(0.6, 0.3, 0.1))
    payload = event.as_dict()

    assert payload["event"] == "rain"
    assert payload["complement"]["T"] == 0.1
    assert payload["complement"]["F"] == 0.6
    assert payload["i_lexicon_projection"]["hierarchy"] == HIERARCHY


def test_probability_sample_space_classification():
    sample = NeutrosophicSampleSpace(
        (
            NeutrosophicEvent("a", NeutrosophicProbability(0.4, 0.2, 0.0)),
            NeutrosophicEvent("b", NeutrosophicProbability(0.4, 0.1, 0.0)),
        )
    ).as_dict()

    assert sample["primary_classification"] == "incomplete_sample_space"
    assert "indeterminate_sample_space" in sample["sample_space_classification"]
    assert sample["operational_tif"]["I"] == 0.15000000000000002


def test_probability_cli_smoke(capsys):
    assert main(["nss", "probability", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == PROBABILITY_SOURCE_URL

    assert main(["nss", "probability", "event", "--name", "rain", "--T", "0.6", "--I", "0.3", "--F", "0.1"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["event"] == "rain"

    events = '[{"name":"a","T":0.4,"I":0.2,"F":0.0},{"name":"b","T":0.4,"I":0.1,"F":0.0}]'
    assert main(["nss", "probability", "sample-space", "--events", events]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["event_count"] == 2
