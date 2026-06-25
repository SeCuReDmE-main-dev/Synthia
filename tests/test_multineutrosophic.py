import json

from synthia_core.cli import main
from synthia_core.multineutrosophic import MULTI_SOURCE_URL, fuse_multineutrosophic_assessments


def test_multineutrosophic_fusion_scores_conflict_and_bounds():
    payload = fuse_multineutrosophic_assessments(
        [
            {"source": "a", "T": 0.8, "I": 0.1, "F": 0.1, "weight": 2},
            {"source": "b", "T": 0.2, "I": 0.6, "F": 0.4, "weight": 1},
        ]
    )

    assert payload["assessment_count"] == 2
    assert payload["fused_components"]["T"] == 0.6
    assert payload["conflict_score"] > 0.0
    assert 0.0 <= payload["fused_tif"]["I_lexicon"] <= 1.0


def test_multineutrosophic_cli_smoke(capsys):
    assert main(["nss", "multi-set", "explain"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source"]["url"] == MULTI_SOURCE_URL

    assessments = '[{"source":"a","T":0.8,"I":0.1,"F":0.1},{"source":"b","T":0.2,"I":0.6,"F":0.4}]'
    assert main(["nss", "multi-set", "fuse", "--assessments", assessments]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["assessment_count"] == 2


def test_i_chain_includes_multineutrosophic_profile(capsys):
    assert main(["lexicon", "i-chain", "classify", "--text", "multi-source expert fusion in multineutrosophic set", "--domain", "math"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["multineutrosophic_profile"]["assessment_count"] == 2
