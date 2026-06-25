import json

from synthia_core.cli import main
from synthia_core.neutrosophic_foundation import (
    FOUNDATION_URL,
    foundation_normalize,
    foundation_profile,
)
from synthia_core.safety import HIERARCHY


def test_foundation_normalization_preserves_formal_and_bounds_operational():
    payload = foundation_normalize(T=1.2, I=0.4, F=-0.1, profile="standard")

    assert payload["formal_value"]["components"]["T"]["formal_value"] == 1.2
    assert payload["formal_value"]["components"]["T"]["was_clamped"] is True
    assert payload["formal_value"]["components"]["F"]["formal_value"] == -0.1
    assert payload["operational_tif"]["T"] == 1.0
    assert payload["operational_tif"]["I"] == 0.4
    assert payload["operational_tif"]["F"] == 0.0
    assert payload["hierarchy"] == HIERARCHY


def test_paradoxist_and_dialetheist_allow_high_truth_and_falsity():
    paradoxist = foundation_normalize(T=0.95, I=0.1, F=0.9, profile="paradoxist")
    dialetheist = foundation_profile("dialetheist")

    assert paradoxist["formal_value"]["allows_high_truth_and_falsity"] is True
    assert paradoxist["operational_tif"]["I_system^S"] >= 0.5
    assert dialetheist["profile"]["allows_high_truth_and_falsity"] is True
    assert dialetheist["operational_tif"]["T"] == 1.0
    assert dialetheist["operational_tif"]["F"] == 1.0


def test_uncertain_profile_increases_system_indeterminacy():
    payload = foundation_normalize(T=0.2, I=0.1, F=0.2, profile="uncertain")

    assert payload["operational_tif"]["I"] == 0.1
    assert payload["operational_tif"]["I_system^S"] == 0.35
    assert payload["operational_tif"]["H_lex"] == 0.35
    assert payload["operational_tif"]["I_lexicon"] == 0.35


def test_foundation_cli_smoke(capsys):
    code = main(["nss", "foundation", "explain"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == FOUNDATION_URL
    assert payload["hierarchy"] == HIERARCHY

    code = main(["nss", "foundation", "normalize", "--T", "1.2", "--I", "0.4", "--F", "-0.1", "--profile", "standard"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["formal_value"]["components"]["T"]["formal_value"] == 1.2
    assert payload["operational_tif"]["T"] == 1.0

    code = main(["nss", "foundation", "profile", "--name", "paradoxist"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["profile"]["name"] == "paradoxist"
    assert payload["formal_value"]["allows_high_truth_and_falsity"] is True


def test_i_chain_classify_includes_foundation_profile_when_relevant(capsys):
    code = main(
        [
            "lexicon",
            "i-chain",
            "classify",
            "--text",
            "neutrosophic probability with uncertain indeterminacy",
            "--domain",
            "ffed_math",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["foundation_profile"]["profile"]["name"] == "uncertain"
    assert payload["selected_layer"] == "I_lexicon"
    assert "D_f" not in json.dumps(payload)
    assert "i_fractal" not in json.dumps(payload)
