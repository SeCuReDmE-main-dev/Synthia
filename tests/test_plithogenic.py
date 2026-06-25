from synthia_core.plithogenic import (
    FractalCarrierProfile,
    PlithogenicAttribute,
    PlithogenicIProfile,
    PlithogenicMatrix,
    SystemIndeterminacyChain,
    TIF,
    classify_i_chain_text,
    render_symbolic_notation,
    resolve_indeterminacy_symbol,
)
from synthia_core.safety import HIERARCHY


def test_tif_bounds_and_hierarchy():
    payload = TIF(T=2.0, I=-1.0, F=0.5, I_system=1.5, H_lex=1.3, G_lex=0.2, I_lexicon=2.0).as_dict()

    assert payload["T"] == 1.0
    assert payload["I"] == 0.0
    assert payload["F"] == 0.5
    assert payload["I_system^S"] == 1.0
    assert payload["H_lex"] == 1.0
    assert payload["G_lex"] == 0.2
    assert payload["I_lexicon"] == 1.0
    assert payload["system_indeterminacy_chain"]["layers"][0]["canonical_id"] == "I"
    assert payload["system_indeterminacy_chain"]["layers"][1]["canonical_id"] == "I_system^S"
    assert payload["system_indeterminacy_chain"]["layers"][2]["canonical_id"] == "H_lex"
    assert payload["system_indeterminacy_chain"]["layers"][3]["canonical_id"] == "G_lex"
    assert payload["system_indeterminacy_chain"]["layers"][4]["canonical_id"] == "I_lexicon"
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
    assert profile["indeterminacy_profile"]["system_indeterminacy_chain"]["carrier_type"] == "lexicon_distribution"
    assert len(profile["feature_vector"]) == 7
    assert profile["hierarchy"] == HIERARCHY


def test_plithogenic_aliases_resolve_to_i_system_without_mutating_canonical():
    assert resolve_indeterminacy_symbol("I_s") == "I_system^S"
    assert resolve_indeterminacy_symbol("I_s_system") == "I_system^S"

    rendered = render_symbolic_notation("I_s", "latex")

    assert rendered["symbol"] == "I_system^S"
    assert rendered["rendered"] == r"I_{\mathrm{system}}^{S}"


def test_i_chain_classifier_uses_lexicon_chain_by_default_and_fractal_only_when_explicit():
    default = classify_i_chain_text("D_f fractal dimension for the system", "ffed_math")
    specialized = classify_i_chain_text("D_f fractal dimension for the system", "fractal_geometry")

    assert default["selected_layer"] == "I_lexicon"
    assert default["carrier_type"] == "lexicon_distribution"
    assert "specialized_carrier" not in default["system_indeterminacy_chain"]
    assert specialized["carrier_type"] == "fractal_geometry"
    assert specialized["chain"]["specialized_carrier"]["carrier_type"] == "fractal_geometry"


def test_plithogenic_profile_keeps_private_evidence_as_metadata_only():
    profile = PlithogenicIProfile().as_dict()

    assert profile["canonical_indeterminacy_class"] == "I_system^S"
    assert "private_evidence_ids" not in profile
    assert "raw_gmail_body" not in str(profile).lower()


def test_fractal_carrier_profile_is_opt_in_specialized_math():
    profile = FractalCarrierProfile(D_f=1.4, dF=0.2, i_fractal=0.7).as_dict()

    assert profile["carrier_type"] == "fractal_geometry"
    assert profile["public_default"] is False
    assert profile["variables"]["D_f"] == 1.4


def test_system_indeterminacy_chain_defaults_to_i_lexicon_carrier():
    chain = SystemIndeterminacyChain.from_tif(TIF(T=0.8, I=0.2, F=0.0, I_system=0.2))

    assert chain.carrier_type == "lexicon_distribution"
    assert chain.as_dict()["layers"][4]["canonical_id"] == "I_lexicon"
