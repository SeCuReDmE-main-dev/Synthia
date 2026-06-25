import json

from synthia_core.cli import main
from synthia_core.neutrosophic_sets import SET_SOURCE_URL, NeutrosophicSetClassifier
from synthia_core.safety import HIERARCHY


def test_set_classifier_consistent_complete_and_ifs_compatible():
    payload = NeutrosophicSetClassifier().classify(0.5, 0.2, 0.3)

    assert payload["primary_classification"] == "consistent_complete"
    assert "intuitionistic_fuzzy_compatible" in payload["set_membership_classification"]
    assert payload["ifs_compatibility"]["is_ifs_compatible"] is True
    assert payload["operational_tif"]["T"] == 0.5
    assert payload["operational_tif"]["I"] == 0.2
    assert payload["operational_tif"]["F"] == 0.3
    assert payload["hierarchy"] == HIERARCHY


def test_set_classifier_incomplete_and_paraconsistent():
    incomplete = NeutrosophicSetClassifier().classify(0.1, 0.3, 0.4)
    paraconsistent = NeutrosophicSetClassifier().classify(0.3, 0.51, 0.28)

    assert incomplete["primary_classification"] == "incomplete"
    assert "intuitionistic_fuzzy_compatible" in incomplete["set_membership_classification"]
    assert paraconsistent["primary_classification"] == "paraconsistent"
    assert "general_neutrosophic" in paraconsistent["set_membership_classification"]


def test_set_classifier_preserves_formal_values_and_clamps_operational():
    payload = NeutrosophicSetClassifier().classify(1.2, -0.2, 1.4)

    classifications = payload["set_membership_classification"]
    assert "over_membership" in classifications
    assert "under_indeterminacy" in classifications
    assert "over_nonmembership" in classifications
    assert payload["formal_value"]["components"]["T"]["formal_value"] == 1.2
    assert payload["formal_value"]["components"]["I"]["formal_value"] == -0.2
    assert payload["formal_value"]["components"]["F"]["formal_value"] == 1.4
    assert payload["operational_tif"]["T"] == 1.0
    assert payload["operational_tif"]["I"] == 0.0
    assert payload["operational_tif"]["F"] == 1.0


def test_ifs_compatibility_rejects_t_plus_f_greater_than_one():
    payload = NeutrosophicSetClassifier().compare_ifs(0.8, 0.1, 0.4)

    assert payload["is_ifs_compatible"] is False
    assert payload["T_plus_F"] == 1.2000000000000002
    assert "IFS compatibility rejected" in payload["reason"]
    assert payload["hierarchy"] == HIERARCHY


def test_set_cli_smoke(capsys):
    code = main(["nss", "set", "explain"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == SET_SOURCE_URL
    assert "paraconsistent" in payload["classification_labels"]

    code = main(["nss", "set", "classify", "--T", "0.3", "--I", "0.51", "--F", "0.28"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["primary_classification"] == "paraconsistent"
    assert payload["source"]["url"] == SET_SOURCE_URL

    code = main(["nss", "set", "compare-ifs", "--T", "0.8", "--I", "0.1", "--F", "0.4"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["is_ifs_compatible"] is False


def test_i_chain_classify_includes_set_membership_profile_when_relevant(capsys):
    code = main(
        [
            "lexicon",
            "i-chain",
            "classify",
            "--text",
            "intuitionistic fuzzy set membership is incomplete",
            "--domain",
            "ffed_math",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["set_membership_profile"]["primary_classification"] == "incomplete"
    assert payload["selected_layer"] == "I_lexicon"
    assert "D_f" not in json.dumps(payload)
    assert "i_fractal" not in json.dumps(payload)
