from synthia_core.plithogenic import PlithogenicAttribute, PlithogenicMatrix, TIF
from synthia_core.safety import HIERARCHY


def test_tif_bounds_and_hierarchy():
    payload = TIF(T=2.0, I=-1.0, F=0.5, I_system=1.5, D_f=1.4, dF=0.2, i_fractal=2.0).as_dict()

    assert payload["T"] == 1.0
    assert payload["I"] == 0.0
    assert payload["F"] == 0.5
    assert payload["I_system^S"] == 1.0
    assert payload["i_fractal"] == 1.0
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
    assert len(profile["feature_vector"]) == 4
    assert profile["hierarchy"] == HIERARCHY
