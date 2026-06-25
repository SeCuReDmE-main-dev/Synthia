import json
from pathlib import Path

from synthia_core.cli import main
from synthia_core.safety import HIERARCHY
from synthia_core.swarm import (
    AntiEntropyTrustLedger,
    DroneNodeApp,
    MissionSafetyGate,
    QueenCoordinator,
    SwarmReviewPacketBuilder,
)


def test_drone_node_builds_candidate_observation(tmp_path: Path):
    image = tmp_path / "amazon_plant_unknown.jpg"
    image.write_bytes(b"field-frame")

    app = DroneNodeApp("drone.pi.1")
    observation = app.ingest_frame(
        image,
        {"latitude": -3.4653, "longitude": -62.2159, "battery_pct": 87},
        [{"label": "plant", "confidence": 0.77}, {"label": "unknown_field_signal", "confidence": 0.33}],
    )

    payload = observation.as_dict()

    assert payload["image_sha256"]
    assert payload["human_review_required"] is True
    assert payload["claim_boundary"].startswith("candidate observation only")
    assert "biology" in payload["lexicon_domains"]
    assert payload["tif"]["hierarchy"] == HIERARCHY


def test_queen_adds_pheromone_ctn_and_identity(tmp_path: Path):
    image = tmp_path / "maya_structure.jpg"
    image.write_bytes(b"field-frame")
    observation = DroneNodeApp("drone.pi.2").ingest_frame(
        image,
        {"latitude": 17.222, "longitude": -89.623, "timestamp": 10},
        [{"label": "structure", "confidence": 0.68}],
    )

    result = QueenCoordinator().ingest_observation(observation)

    assert result["identity_envelope"]["identity_digest"]
    assert result["contextual_trust"]["trust"] > 0.0
    assert result["pheromone_cell"]["observation_ids"] == [observation.observation_id]
    assert result["task_hints"][0]["actuation_allowed"] is False


def test_review_packet_uses_candidate_and_sensitive_location_boundary(tmp_path: Path):
    image = tmp_path / "frog.jpg"
    image.write_bytes(b"field-frame")
    observation = DroneNodeApp("drone.pi.3").ingest_frame(
        image,
        {"latitude": -3.46539, "longitude": -62.21591},
        [{"label": "frog", "confidence": 0.81}],
    )

    packet = SwarmReviewPacketBuilder().build(observation)

    assert packet["candidate_language_only"] is True
    assert packet["observation"]["telemetry"]["latitude"] == -3.465
    assert packet["human_authority_boundary"].startswith("Synthia does not declare")


def test_safety_gate_keeps_v1_passive_even_with_prerequisites():
    result = MissionSafetyGate().evaluate(
        {
            "simulation_passed": True,
            "geofence_id": "geo-1",
            "human_pilot_approval": True,
            "legal_authorization": True,
            "land_permission": True,
        }
    )

    assert result["future_actuation_prerequisites_present"] is True
    assert result["actuation_allowed"] is False
    assert result["v1_policy"] == "passive_observation_only"


def test_anti_entropy_rejects_stale_node_state():
    ledger = AntiEntropyTrustLedger()
    assert ledger.upsert("drone.pi.4", {"trust": 0.8}, version=2)["accepted"] is True
    assert ledger.upsert("drone.pi.4", {"trust": 0.2}, version=1)["accepted"] is False
    assert ledger.records["drone.pi.4"]["trust"] == 0.8


def test_cli_swarm_ingest_frame_smoke(tmp_path: Path, capsys):
    image = tmp_path / "tree.jpg"
    image.write_bytes(b"field-frame")

    code = main(
        [
            "swarm",
            "ingest-frame",
            "--image",
            str(image),
            "--telemetry",
            json.dumps({"latitude": 1.1, "longitude": 2.2}),
            "--detection",
            "tree:0.74",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["observation"]["lexicon_domains"] == ["biology"]
    assert payload["contextual_trust"]["middleware_attack_boundary"]


def test_cli_swarm_safety_check_smoke(capsys):
    code = main(["swarm", "safety-check", "--mission", '{"simulation_passed": false}'])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["actuation_allowed"] is False
    assert "simulation_passed" in payload["missing_prerequisites"]

