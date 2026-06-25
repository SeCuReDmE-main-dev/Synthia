from synthia_core.plithogenic import (
    PlithogenicAttribute,
    PlithogenicIProfile,
    PlithogenicMatrix,
    TIF,
    classify_i_chain_text,
    render_symbolic_notation,
    resolve_indeterminacy_symbol,
)
from synthia_core.safety import HIERARCHY


def test_tif_bounds_and_hierarchy():
    payload = TIF(T=2.0, I=-1.0, F=0.5, I_system=1.5, D_f=1.4, dF=0.2, i_fractal=2.0).as_dict()

    assert payload["T"] == 1.0
    assert payload["I"] == 0.0
    assert payload["F"] == 0.5
    assert payload["I_system^S"] == 1.0
    assert payload["i_fractal"] == 1.0
    assert payload["indeterminacy_chain"]["layers"][0]["canonical_id"] == "I"
    assert payload["indeterminacy_chain"]["layers"][1]["canonical_id"] == "I_system^S"
    assert payload["indeterminacy_chain"]["layers"][2]["canonical_id"] == "D_f"
    assert payload["indeterminacy_chain"]["layers"][3]["canonical_id"] == "dF"
    assert payload["indeterminacy_chain"]["layers"][4]["canonical_id"] == "i_fractal"
    assert payload["hierarchy"] == HIERARCHY


def test_plithogenic_matrix_reports_contradiction_and_features():
    matrix = PlithogenicMatrix(
        [
            PlithogenicAttribute("diagnosis", "stable", TIF(T=0.9, I=0.1, F=0.0)),
            PlithogenicAttribute("diagnosis", "contested", TIF(T=0.2, I=0.5, F=0.4)),
        ]
    )

    profile = matrix.profile()

    assert profile["contradiction_summary"]["max_degree"] > 0.0
    assert profile["plithogenic_classified_as"] == "I_system^S"
    assert profile["indeterminacy_profile"]["plithogenic_i_profile"]["canonical_indeterminacy_class"] == "I_system^S"
    assert len(profile["feature_vector"]) == 4
    assert profile["hierarchy"] == HIERARCHY


def test_plithogenic_aliases_resolve_to_i_system_without_mutating_canonical():
    assert resolve_indeterminacy_symbol("I_s") == "I_system^S"
    assert resolve_indeterminacy_symbol("I_s_system") == "I_system^S"

    rendered = render_symbolic_notation("I_s", "latex")

    assert rendered["symbol"] == "I_system^S"
    assert rendered["rendered"] == r"I_{\mathrm{system}}^{S}"


def test_i_chain_classifier_preserves_distinct_fractal_layers():
    dimension = classify_i_chain_text("D_f fractal dimension for the system", "ffed_math")
    drift = classify_i_chain_text("dF delta fractal drift", "ffed_math")
    recursive = classify_i_chain_text("recursive i_fractal classification", "ffed_math")

    assert dimension["selected_layer"] == "D_f"
    assert drift["selected_layer"] == "dF"
    assert recursive["selected_layer"] == "i_fractal"


def test_plithogenic_profile_keeps_private_evidence_as_metadata_only():
    profile = PlithogenicIProfile().as_dict()

    assert profile["canonical_indeterminacy_class"] == "I_system^S"
    assert profile["private_evidence_ids"] == ["gmail.thread.19edbb1c9fd0030e"]
    assert "raw_gmail_body" not in str(profile).lower()
