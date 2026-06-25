from synthia_core.lexicon import seed_base_lexicon
from synthia_core.safety import HIERARCHY


def test_seed_lexicon_classifies_taxonomic_memory_repair():
    lexicon = seed_base_lexicon()

    result = lexicon.classify_text(
        "Taxonomic memory repair helps species as systems preserve redescription.",
        "phylocode_nomenclature",
    )

    assert result["hierarchy"] == HIERARCHY
    assert [item["term"] for item in result["matched_terms"]] == ["taxonomic memory repair"]
    assert result["matched_terms"][0]["i_lexicon"]["indeterminacy_layer"] == "I_system^S"
    assert result["i_lexicon_classification"]["plithogenic_classified_as"] == "I_system^S"
    assert result["plithogenic_profile"]["weighted_cumulative_truth"]["T"] > 0.8


def test_lexicon_switch_preserves_bridge_context():
    lexicon = seed_base_lexicon()

    trace = lexicon.switch_context("taxonomy", "phylocode_nomenclature", "ctx-1").as_dict()

    assert trace["from_domain"] == "taxonomy"
    assert trace["to_domain"] == "phylocode_nomenclature"
    assert trace["bridge_ids"] == [0]
    assert trace["i_lexicon_switch_state"]["plithogenic_classified_as"] == "I_system^S"
    assert trace["hierarchy"] == HIERARCHY
