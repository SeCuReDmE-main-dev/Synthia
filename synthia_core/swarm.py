"""Simulation-first swarm field scout core for Synthia.

The swarm layer is deliberately passive in this milestone. It can ingest
telemetry, image evidence, and vision detections, but it cannot command flight.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping
from uuid import uuid4

from .lexicon import ILexicon, LexiconDomain, LexiconNode, seed_base_lexicon
from .plithogenic import PlithogenicAttribute, PlithogenicMatrix, TIF, clamp01
from .safety import HIERARCHY


BIOLOGY_MARKERS = {
    "animal",
    "bird",
    "fish",
    "frog",
    "insect",
    "mammal",
    "plant",
    "tree",
    "flower",
    "fungus",
    "leaf",
}
ARCHAEOLOGY_MARKERS = {"maya", "ruin", "structure", "wall", "temple", "mound", "stone", "road"}
PHYSICS_MARKERS = {"thermal", "magnetic", "spectral", "radiation", "signal", "anomaly"}
RISK_MARKERS = {"person", "vehicle", "powerline", "fire", "smoke", "restricted", "hazard"}


def _now() -> float:
    return time.time()


def _round_coordinate(value: float | None, precision: int = 3) -> float | None:
    if value is None:
        return None
    return round(value, precision)


def hash_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class TelemetrySnapshot:
    node_id: str
    timestamp: float = field(default_factory=_now)
    latitude: float | None = None
    longitude: float | None = None
    altitude_m: float | None = None
    heading_deg: float | None = None
    battery_pct: float | None = None
    source: str = "simulated"
    flight_stack: str = "unknown"
    flight_mode: str = "observe_only"
    armed: bool = False

    def as_dict(self, public_safe: bool = False) -> dict[str, object]:
        latitude = _round_coordinate(self.latitude) if public_safe else self.latitude
        longitude = _round_coordinate(self.longitude) if public_safe else self.longitude
        return {
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude_m": self.altitude_m,
            "heading_deg": self.heading_deg,
            "battery_pct": self.battery_pct,
            "source": self.source,
            "flight_stack": self.flight_stack,
            "flight_mode": self.flight_mode,
            "armed": self.armed,
        }


@dataclass(frozen=True)
class VisionDetection:
    label: str
    confidence: float
    source: str = "manual_or_simulated"
    box_xyxy: tuple[float, float, float, float] | None = None

    def tif(self) -> TIF:
        confidence = clamp01(self.confidence)
        indeterminacy = clamp01(1.0 - confidence)
        return TIF(
            T=confidence,
            I=indeterminacy,
            F=0.0,
            I_system=indeterminacy,
            D_f=indeterminacy,
            dF=indeterminacy / 2,
            i_fractal=indeterminacy,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "confidence": clamp01(self.confidence),
            "source": self.source,
            "box_xyxy": list(self.box_xyxy) if self.box_xyxy else None,
            "tif": self.tif().as_dict(),
        }


@dataclass(frozen=True)
class ObservationPacket:
    node_id: str
    telemetry: TelemetrySnapshot
    image_uri: str
    image_sha256: str | None = None
    detections: tuple[VisionDetection, ...] = ()
    observation_id: str = field(default_factory=lambda: f"obs.{uuid4().hex}")
    captured_at: float = field(default_factory=_now)
    lexicon_domains: tuple[str, ...] = ()
    novelty_score: float = 0.0
    risk_score: float = 0.0

    def tif(self) -> TIF:
        if not self.detections:
            return TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, D_f=1.0, dF=0.5, i_fractal=1.0)
        profile = PlithogenicMatrix(
            [
                PlithogenicAttribute(
                    name=detection.label,
                    value="field_detection",
                    tif=detection.tif(),
                    weight=detection.confidence,
                    source_id=detection.source,
                )
                for detection in self.detections
            ]
        ).weighted_cumulative_truth()
        return TIF(
            T=profile["T"],
            I=max(profile["I"], self.novelty_score),
            F=profile["F"],
            I_system=max(profile["I"], self.novelty_score),
            D_f=self.novelty_score,
            dF=max(0.0, self.novelty_score - profile["T"] / 2),
            i_fractal=max(profile["I"], self.novelty_score),
        )

    def as_dict(self, public_safe: bool = True) -> dict[str, object]:
        return {
            "observation_id": self.observation_id,
            "node_id": self.node_id,
            "captured_at": self.captured_at,
            "image_uri": self.image_uri,
            "image_sha256": self.image_sha256,
            "image_mime": mimetypes.guess_type(self.image_uri)[0],
            "telemetry": self.telemetry.as_dict(public_safe=public_safe),
            "detections": [item.as_dict() for item in self.detections],
            "lexicon_domains": list(self.lexicon_domains),
            "novelty_score": self.novelty_score,
            "risk_score": self.risk_score,
            "tif": self.tif().as_dict(),
            "human_review_required": True,
            "claim_boundary": "candidate observation only; not a species, structure, or hazard claim",
            "hierarchy": HIERARCHY,
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "ObservationPacket":
        telemetry_payload = payload.get("telemetry") if isinstance(payload.get("telemetry"), Mapping) else {}
        detections_payload = payload.get("detections") if isinstance(payload.get("detections"), list) else []
        return cls(
            node_id=str(payload.get("node_id", telemetry_payload.get("node_id", "unknown"))),
            telemetry=TelemetrySnapshot(
                node_id=str(telemetry_payload.get("node_id", payload.get("node_id", "unknown"))),
                timestamp=float(telemetry_payload.get("timestamp", payload.get("captured_at", _now()))),
                latitude=_optional_payload_float(telemetry_payload, "latitude"),
                longitude=_optional_payload_float(telemetry_payload, "longitude"),
                altitude_m=_optional_payload_float(telemetry_payload, "altitude_m"),
                heading_deg=_optional_payload_float(telemetry_payload, "heading_deg"),
                battery_pct=_optional_payload_float(telemetry_payload, "battery_pct"),
                source=str(telemetry_payload.get("source", "stored")),
                flight_stack=str(telemetry_payload.get("flight_stack", "unknown")),
                flight_mode=str(telemetry_payload.get("flight_mode", "observe_only")),
                armed=bool(telemetry_payload.get("armed", False)),
            ),
            image_uri=str(payload.get("image_uri", "")),
            image_sha256=None if payload.get("image_sha256") is None else str(payload.get("image_sha256")),
            detections=tuple(
                VisionDetection(
                    label=str(item.get("label", "unknown")),
                    confidence=float(item.get("confidence", 0.5)),
                    source=str(item.get("source", "stored")),
                    box_xyxy=tuple(item["box_xyxy"]) if item.get("box_xyxy") else None,
                )
                for item in detections_payload
                if isinstance(item, Mapping)
            ),
            observation_id=str(payload.get("observation_id", f"obs.{uuid4().hex}")),
            captured_at=float(payload.get("captured_at", _now())),
            lexicon_domains=tuple(str(item) for item in payload.get("lexicon_domains", []) if item),
            novelty_score=float(payload.get("novelty_score", 0.0)),
            risk_score=float(payload.get("risk_score", 0.0)),
        )


def _optional_payload_float(payload: Mapping[str, object], key: str) -> float | None:
    if key not in payload or payload[key] is None:
        return None
    return float(payload[key])


class MAVLinkTelemetryAdapter:
    """Normalize MAVLink-like telemetry dictionaries without a hard dependency."""

    def parse(self, node_id: str, payload: Mapping[str, object]) -> TelemetrySnapshot:
        return TelemetrySnapshot(
            node_id=node_id,
            timestamp=float(payload.get("timestamp", _now())),
            latitude=self._optional_float(payload, "latitude", "lat"),
            longitude=self._optional_float(payload, "longitude", "lon", "lng"),
            altitude_m=self._optional_float(payload, "altitude_m", "alt", "relative_alt"),
            heading_deg=self._optional_float(payload, "heading_deg", "heading"),
            battery_pct=self._optional_float(payload, "battery_pct", "battery", "battery_remaining"),
            source=str(payload.get("source", "simulated_mavlink")),
            flight_stack=str(payload.get("flight_stack", payload.get("autopilot", "unknown"))),
            flight_mode=str(payload.get("flight_mode", payload.get("mode", "observe_only"))),
            armed=bool(payload.get("armed", False)),
        )

    @staticmethod
    def _optional_float(payload: Mapping[str, object], *keys: str) -> float | None:
        for key in keys:
            if key not in payload or payload[key] is None:
                continue
            return float(payload[key])
        return None


class CPAIOnboardVisionAdapter:
    """Small local-vision adapter.

    This object accepts explicit detections for tests/simulation. It also has a
    filename heuristic so the CLI can run offline before a CodeProject.AI server
    or Raspberry Pi is attached.
    """

    def __init__(self, endpoint: str | None = None) -> None:
        self.endpoint = endpoint

    def detect_image(self, image_path: str | Path, detections: Iterable[Mapping[str, object]] | None = None) -> list[VisionDetection]:
        if detections is not None:
            return [
                VisionDetection(
                    label=str(item.get("label", "unknown")),
                    confidence=float(item.get("confidence", 0.5)),
                    source=str(item.get("source", "manual_or_simulated")),
                    box_xyxy=tuple(item["box_xyxy"]) if item.get("box_xyxy") else None,
                )
                for item in detections
            ]

        name = Path(image_path).stem.lower().replace("-", "_")
        inferred: list[VisionDetection] = []
        for marker in sorted(BIOLOGY_MARKERS | ARCHAEOLOGY_MARKERS | PHYSICS_MARKERS | RISK_MARKERS):
            if marker in name:
                inferred.append(VisionDetection(marker, 0.62, source="filename_heuristic"))
        return inferred or [VisionDetection("unknown_field_signal", 0.35, source="filename_heuristic")]


class FieldLexiconClassifier:
    """Map field detections into Synthia lexicon domains."""

    def __init__(self, lexicon: ILexicon | None = None) -> None:
        self.lexicon = lexicon or seed_base_lexicon()

    def classify_detection(self, detection: VisionDetection) -> LexiconNode:
        label = detection.label.lower()
        if label in BIOLOGY_MARKERS:
            domain = LexiconDomain.BIOLOGY.value
            node_type = "field_biology_candidate"
        elif label in ARCHAEOLOGY_MARKERS:
            domain = LexiconDomain.ARCHAEOLOGY.value
            node_type = "field_archaeology_candidate"
        elif label in PHYSICS_MARKERS:
            domain = LexiconDomain.PHYSICS.value
            node_type = "field_physics_signal"
        elif label in RISK_MARKERS:
            domain = LexiconDomain.GENERAL.value
            node_type = "field_risk_signal"
        else:
            domain = LexiconDomain.GENERAL.value
            node_type = "unknown_field_candidate"
        return self.lexicon.add_node(
            LexiconNode(
                term=detection.label,
                domain=domain,
                node_type=node_type,
                definition=f"Passive swarm field observation candidate: {detection.label}",
                source_ids=("swarm.passive_observation",),
                tif=detection.tif(),
            )
        )

    def classify_observation(self, detections: Iterable[VisionDetection]) -> tuple[str, ...]:
        domains = [self.classify_detection(detection).domain for detection in detections]
        return tuple(dict.fromkeys(domains or [LexiconDomain.GENERAL.value]))


class NoveltyCandidateDetector:
    def score(self, detections: Iterable[VisionDetection]) -> float:
        detections = list(detections)
        if not detections:
            return 1.0
        unknown_load = sum(1 for item in detections if "unknown" in item.label.lower())
        uncertainty = max(1.0 - clamp01(item.confidence) for item in detections)
        return clamp01(max(unknown_load / len(detections), uncertainty))


class RiskSignalDetector:
    def score(self, detections: Iterable[VisionDetection]) -> float:
        detections = list(detections)
        if not detections:
            return 0.0
        risk_hits = [
            clamp01(item.confidence)
            for item in detections
            if item.label.lower().strip() in RISK_MARKERS
        ]
        return max(risk_hits or [0.0])


@dataclass
class PheromoneCell:
    cell_id: str
    latitude: float | None
    longitude: float | None
    coverage: float = 0.0
    novelty: float = 0.0
    risk: float = 0.0
    last_seen: float = field(default_factory=_now)
    observation_ids: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coverage": clamp01(self.coverage),
            "novelty": clamp01(self.novelty),
            "risk": clamp01(self.risk),
            "last_seen": self.last_seen,
            "observation_ids": list(self.observation_ids),
        }


class DigitalPheromoneMap:
    def __init__(self, precision: int = 3) -> None:
        self.precision = precision
        self.cells: dict[str, PheromoneCell] = {}

    def cell_key(self, telemetry: TelemetrySnapshot) -> str:
        lat = _round_coordinate(telemetry.latitude, self.precision)
        lon = _round_coordinate(telemetry.longitude, self.precision)
        if lat is None or lon is None:
            return "unknown-location"
        return f"{lat:.{self.precision}f},{lon:.{self.precision}f}"

    def ingest(self, observation: ObservationPacket) -> PheromoneCell:
        key = self.cell_key(observation.telemetry)
        cell = self.cells.setdefault(
            key,
            PheromoneCell(
                cell_id=key,
                latitude=_round_coordinate(observation.telemetry.latitude, self.precision),
                longitude=_round_coordinate(observation.telemetry.longitude, self.precision),
            ),
        )
        cell.coverage = clamp01(cell.coverage + 0.2)
        cell.novelty = clamp01(max(cell.novelty, observation.novelty_score))
        cell.risk = clamp01(max(cell.risk, observation.risk_score))
        cell.last_seen = _now()
        cell.observation_ids.append(observation.observation_id)
        return cell

    def decay(self, factor: float = 0.9) -> None:
        factor = clamp01(factor)
        for cell in self.cells.values():
            cell.coverage *= factor
            cell.novelty *= factor
            cell.risk *= factor

    def task_hints(self, limit: int = 5) -> list[dict[str, object]]:
        ranked = sorted(
            self.cells.values(),
            key=lambda cell: (cell.risk, -cell.novelty, cell.coverage),
        )
        hints: list[dict[str, object]] = []
        for cell in ranked[:limit]:
            if cell.risk >= 0.65:
                action = "avoid_until_human_review"
            elif cell.novelty >= 0.5:
                action = "revisit_for_evidence"
            elif cell.coverage < 0.4:
                action = "increase_coverage"
            else:
                action = "monitor_decay"
            hints.append({"cell": cell.as_dict(), "action": action, "actuation_allowed": False})
        return hints

    def as_geojson(self) -> dict[str, object]:
        features = []
        for cell in self.cells.values():
            geometry = None
            if cell.latitude is not None and cell.longitude is not None:
                geometry = {"type": "Point", "coordinates": [cell.longitude, cell.latitude]}
            features.append({"type": "Feature", "geometry": geometry, "properties": cell.as_dict()})
        return {"type": "FeatureCollection", "features": features}


class FloatingLocationVerifier:
    """Trust location by motion continuity instead of one static GPS point."""

    def __init__(self, max_reasonable_speed_mps: float = 35.0) -> None:
        self.max_reasonable_speed_mps = max_reasonable_speed_mps
        self.last_by_node: dict[str, TelemetrySnapshot] = {}

    def verify(self, telemetry: TelemetrySnapshot) -> dict[str, object]:
        previous = self.last_by_node.get(telemetry.node_id)
        self.last_by_node[telemetry.node_id] = telemetry
        if previous is None or None in {
            previous.latitude,
            previous.longitude,
            telemetry.latitude,
            telemetry.longitude,
        }:
            return {
                "trust": 0.65,
                "status": "baseline_established",
                "floating": True,
                "reason": "first usable location sample or incomplete coordinates",
            }

        distance_m = _flat_distance_m(
            previous.latitude,
            previous.longitude,
            telemetry.latitude,
            telemetry.longitude,
        )
        elapsed = max(telemetry.timestamp - previous.timestamp, 0.001)
        speed_mps = distance_m / elapsed
        over_limit = speed_mps > self.max_reasonable_speed_mps
        return {
            "trust": 0.25 if over_limit else 0.9,
            "status": "location_jump_detected" if over_limit else "location_continuity_ok",
            "floating": True,
            "distance_m": distance_m,
            "elapsed_s": elapsed,
            "speed_mps": speed_mps,
            "max_reasonable_speed_mps": self.max_reasonable_speed_mps,
        }


def _flat_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Equirectangular approximation is enough for local continuity checks.
    mean_lat_scale = 111_320.0
    x = (lon2 - lon1) * mean_lat_scale
    y = (lat2 - lat1) * mean_lat_scale
    return (x * x + y * y) ** 0.5


class FfeDIdentityEnvelope:
    """Non-cryptographic identity envelope until a formal FfeD spec exists."""

    def sign_observation(self, observation: ObservationPacket, node_secret_hint: str = "") -> dict[str, object]:
        material = "|".join(
            [
                observation.node_id,
                observation.observation_id,
                observation.image_sha256 or "",
                node_secret_hint,
            ]
        )
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
        return {
            "node_id": observation.node_id,
            "observation_id": observation.observation_id,
            "identity_digest": digest,
            "ffed_role": "unique identification placeholder",
            "cryptographic_boundary": "not a custom encryption scheme; replace with audited cryptography before field security use",
        }


class ContextualTrustNetwork:
    """Score node trust from location, risk, identity, and state consistency."""

    def __init__(self, floating: FloatingLocationVerifier | None = None) -> None:
        self.floating = floating or FloatingLocationVerifier()
        self.trust_by_node: dict[str, float] = {}

    def score(self, observation: ObservationPacket, identity_envelope: Mapping[str, object] | None = None) -> dict[str, object]:
        location = self.floating.verify(observation.telemetry)
        identity_present = bool(identity_envelope and identity_envelope.get("identity_digest"))
        detection_quality = observation.tif().bounded().T
        risk_penalty = observation.risk_score * 0.35
        identity_bonus = 0.1 if identity_present else 0.0
        trust = clamp01((float(location["trust"]) + detection_quality) / 2 + identity_bonus - risk_penalty)
        self.trust_by_node[observation.node_id] = trust
        return {
            "node_id": observation.node_id,
            "trust": trust,
            "location_verification": location,
            "identity_present": identity_present,
            "risk_penalty": risk_penalty,
            "middleware_attack_boundary": "low trust can quarantine observations; it does not authorize autonomous counter-action",
        }


class AntiEntropyTrustLedger:
    """Merge distributed swarm state without letting stale nodes dominate."""

    def __init__(self) -> None:
        self.node_versions: dict[str, int] = {}
        self.records: dict[str, dict[str, object]] = {}

    def upsert(self, node_id: str, record: Mapping[str, object], version: int | None = None) -> dict[str, object]:
        next_version = version if version is not None else self.node_versions.get(node_id, 0) + 1
        current_version = self.node_versions.get(node_id, 0)
        accepted = next_version >= current_version
        if accepted:
            self.node_versions[node_id] = next_version
            self.records[node_id] = dict(record)
        return {
            "node_id": node_id,
            "accepted": accepted,
            "version": self.node_versions.get(node_id, current_version),
            "anti_entropy": True,
        }

    def reconcile(self, remote_records: Iterable[Mapping[str, object]]) -> dict[str, object]:
        accepted = []
        rejected = []
        for item in remote_records:
            node_id = str(item.get("node_id", "unknown"))
            version = int(item.get("version", 0))
            result = self.upsert(node_id, item, version=version)
            (accepted if result["accepted"] else rejected).append(result)
        return {
            "accepted": accepted,
            "rejected_stale": rejected,
            "node_versions": dict(self.node_versions),
            "state_consistency": "eventual_consistency_for_trust_state",
        }


@dataclass(frozen=True)
class RethinkDBBackendConfig:
    host: str = "127.0.0.1"
    port: int = 28015
    database: str = "synthia_swarm"
    observations_table: str = "observations"
    heartbeats_table: str = "heartbeats"
    trust_table: str = "trust_state"
    executable: str | None = None
    data_dir: str | None = None


class RethinkDBSwarmBackend:
    """Optional RethinkDB backend for CTN and anti-entropy swarm state."""

    def __init__(self, config: RethinkDBBackendConfig | None = None) -> None:
        self.config = config or RethinkDBBackendConfig()

    def status(self) -> dict[str, object]:
        try:
            r = self._driver()
            conn = self._connect(r)
            try:
                dbs = r.db_list().run(conn)
            finally:
                conn.close()
            return {
                "backend": "rethinkdb",
                "available": True,
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "database_exists": self.config.database in dbs,
                "executable": self.config.executable,
                "data_dir": self.config.data_dir,
            }
        except Exception as exc:
            return {
                "backend": "rethinkdb",
                "available": False,
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
                "error": f"{type(exc).__name__}: {exc}",
                "executable": self.config.executable,
                "data_dir": self.config.data_dir,
            }

    def ensure_schema(self) -> dict[str, object]:
        r = self._driver()
        conn = self._connect(r, db=None)
        try:
            if self.config.database not in r.db_list().run(conn):
                r.db_create(self.config.database).run(conn)
            db = r.db(self.config.database)
            existing = db.table_list().run(conn)
            created = []
            for table in (self.config.observations_table, self.config.heartbeats_table, self.config.trust_table):
                if table not in existing:
                    db.table_create(table).run(conn)
                    created.append(table)
            return {"database": self.config.database, "created_tables": created, "ready": True}
        finally:
            conn.close()

    def store_observation(self, observation: ObservationPacket, extra: Mapping[str, object] | None = None) -> dict[str, object]:
        r = self._driver()
        conn = self._connect(r)
        document = observation.as_dict(public_safe=False)
        document["id"] = observation.observation_id
        document["extra"] = dict(extra or {})
        try:
            result = r.table(self.config.observations_table).insert(document, conflict="replace").run(conn)
            return {"stored": True, "backend": "rethinkdb", "result": result, "observation_id": observation.observation_id}
        finally:
            conn.close()

    def store_heartbeat(self, node_id: str, status: Mapping[str, object]) -> dict[str, object]:
        r = self._driver()
        conn = self._connect(r)
        document = {"id": node_id, "node_id": node_id, "last_seen": _now(), "status": dict(status)}
        try:
            result = r.table(self.config.heartbeats_table).insert(document, conflict="replace").run(conn)
            return {"stored": True, "backend": "rethinkdb", "result": result, "node_id": node_id}
        finally:
            conn.close()

    def load_observation(self, observation_id: str) -> ObservationPacket | None:
        r = self._driver()
        conn = self._connect(r)
        try:
            document = r.table(self.config.observations_table).get(observation_id).run(conn)
        finally:
            conn.close()
        if not document:
            return None
        return ObservationPacket.from_mapping(document)

    def _driver(self):
        import rethinkdb  # type: ignore

        if hasattr(rethinkdb, "connect"):
            return rethinkdb
        if hasattr(rethinkdb, "r"):
            return rethinkdb.r
        if hasattr(rethinkdb, "RethinkDB"):
            return rethinkdb.RethinkDB()
        raise RuntimeError("unsupported rethinkdb Python driver shape")

    def _connect(self, r, db: str | None | object = ...):
        target_db = self.config.database if db is ... else db
        kwargs = {"host": self.config.host, "port": self.config.port}
        if target_db:
            kwargs["db"] = target_db
        return r.connect(**kwargs)


class EvidenceVault:
    """Private evidence storage for observations and media outside the public repo."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.observations_dir = self.root / "observations"
        self.media_dir = self.root / "media"
        self.notes_dir = self.root / "notes"

    @classmethod
    def from_private_org(cls, private_org: str | Path) -> "EvidenceVault":
        return cls(Path(private_org) / "private_evidence" / "swarm")

    def ensure(self) -> None:
        self.observations_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    def store_observation(
        self,
        observation: ObservationPacket,
        private_note: str = "",
        copy_media: bool = True,
    ) -> dict[str, object]:
        self.ensure()
        payload = observation.as_dict(public_safe=False)
        stored_media_path = None
        source = Path(observation.image_uri)
        if copy_media and source.exists() and source.is_file():
            media_name = f"{observation.observation_id}_{observation.image_sha256 or hash_file(source)}{source.suffix}"
            target = self.media_dir / media_name
            shutil.copy2(source, target)
            stored_media_path = str(target)
        payload["private_note"] = private_note
        payload["stored_media_path"] = stored_media_path
        payload["public_repo_boundary"] = "private field evidence remains outside the public Synthia repository"
        path = self.observations_dir / f"{observation.observation_id}.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"stored": True, "path": str(path), "stored_media_path": stored_media_path}

    def load_observation(self, observation_id: str) -> ObservationPacket:
        path = self.observations_dir / f"{observation_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"observation not found in evidence vault: {observation_id}")
        return ObservationPacket.from_mapping(json.loads(path.read_text(encoding="utf-8")))


class OfflineObservationBuffer:
    """Deduplicate and replay observations after node or mesh interruption."""

    def __init__(self) -> None:
        self._queued: dict[str, ObservationPacket] = {}
        self._acked: set[str] = set()

    def enqueue(self, observation: ObservationPacket) -> dict[str, object]:
        duplicate = observation.observation_id in self._queued or observation.observation_id in self._acked
        if not duplicate:
            self._queued[observation.observation_id] = observation
        return {"observation_id": observation.observation_id, "queued": not duplicate, "duplicate": duplicate}

    def mark_acked(self, observation_id: str) -> None:
        self._queued.pop(observation_id, None)
        self._acked.add(observation_id)

    def replay(self, queen: "QueenCoordinator") -> dict[str, object]:
        replayed = []
        for observation_id, observation in list(self._queued.items()):
            replayed.append(queen.ingest_observation(observation))
            self.mark_acked(observation_id)
        return {"replayed_count": len(replayed), "results": replayed}

    def status(self) -> dict[str, object]:
        return {"queued_count": len(self._queued), "acked_count": len(self._acked)}


class DroneNodeApp:
    def __init__(
        self,
        node_id: str,
        vision: CPAIOnboardVisionAdapter | None = None,
        telemetry: MAVLinkTelemetryAdapter | None = None,
        classifier: FieldLexiconClassifier | None = None,
    ) -> None:
        self.node_id = node_id
        self.vision = vision or CPAIOnboardVisionAdapter()
        self.telemetry = telemetry or MAVLinkTelemetryAdapter()
        self.classifier = classifier or FieldLexiconClassifier()
        self.novelty = NoveltyCandidateDetector()
        self.risk = RiskSignalDetector()

    def ingest_frame(
        self,
        image_path: str | Path,
        telemetry_payload: Mapping[str, object],
        detections: Iterable[Mapping[str, object]] | None = None,
    ) -> ObservationPacket:
        path = Path(image_path)
        detected = self.vision.detect_image(path, detections=detections)
        domains = self.classifier.classify_observation(detected)
        return ObservationPacket(
            node_id=self.node_id,
            telemetry=self.telemetry.parse(self.node_id, telemetry_payload),
            image_uri=str(path),
            image_sha256=hash_file(path) if path.exists() and path.is_file() else None,
            detections=tuple(detected),
            lexicon_domains=domains,
            novelty_score=self.novelty.score(detected),
            risk_score=self.risk.score(detected),
        )


class QueenCoordinator:
    def __init__(
        self,
        pheromone_map: DigitalPheromoneMap | None = None,
        evidence_vault: EvidenceVault | None = None,
        rethinkdb_backend: RethinkDBSwarmBackend | None = None,
    ) -> None:
        self.pheromone_map = pheromone_map or DigitalPheromoneMap()
        self.nodes: dict[str, dict[str, object]] = {}
        self.observations: dict[str, ObservationPacket] = {}
        self.identity = FfeDIdentityEnvelope()
        self.ctn = ContextualTrustNetwork()
        self.anti_entropy = AntiEntropyTrustLedger()
        self.evidence_vault = evidence_vault
        self.rethinkdb_backend = rethinkdb_backend

    def heartbeat(self, node_id: str, status: Mapping[str, object] | None = None) -> dict[str, object]:
        payload = {
            "node_id": node_id,
            "last_seen": _now(),
            "status": dict(status or {}),
            "actuation_allowed": False,
        }
        self.nodes[node_id] = payload
        if self.rethinkdb_backend is not None:
            try:
                payload["rethinkdb"] = self.rethinkdb_backend.store_heartbeat(node_id, payload["status"])
            except Exception as exc:
                payload["rethinkdb"] = {"stored": False, "error": f"{type(exc).__name__}: {exc}"}
        return payload

    def ingest_observation(self, observation: ObservationPacket) -> dict[str, object]:
        self.observations[observation.observation_id] = observation
        cell = self.pheromone_map.ingest(observation)
        identity_envelope = self.identity.sign_observation(observation)
        trust = self.ctn.score(observation, identity_envelope)
        self.anti_entropy.upsert(
            observation.node_id,
            {
                "node_id": observation.node_id,
                "last_observation_id": observation.observation_id,
                "trust": trust["trust"],
                "cell_id": cell.cell_id,
            },
        )
        storage: dict[str, object] = {}
        if self.evidence_vault is not None:
            storage["evidence_vault"] = self.evidence_vault.store_observation(observation)
        if self.rethinkdb_backend is not None:
            try:
                storage["rethinkdb"] = self.rethinkdb_backend.store_observation(
                    observation,
                    extra={"trust": trust, "pheromone_cell": cell.as_dict()},
                )
            except Exception as exc:
                storage["rethinkdb"] = {"stored": False, "error": f"{type(exc).__name__}: {exc}"}
        return {
            "observation": observation.as_dict(),
            "identity_envelope": identity_envelope,
            "contextual_trust": trust,
            "pheromone_cell": cell.as_dict(),
            "storage": storage,
            "task_hints": self.pheromone_map.task_hints(),
        }

    def status(self) -> dict[str, object]:
        return {
            "nodes": list(self.nodes.values()),
            "observation_count": len(self.observations),
            "pheromone_cells": [cell.as_dict() for cell in self.pheromone_map.cells.values()],
            "task_hints": self.pheromone_map.task_hints(),
            "trust_by_node": dict(self.ctn.trust_by_node),
            "anti_entropy_versions": dict(self.anti_entropy.node_versions),
            "actuation_allowed": False,
            "safety_boundary": "queen coordinator emits task hints only in this milestone",
        }

    def find_observation(self, observation_id: str) -> ObservationPacket | None:
        if observation_id in self.observations:
            return self.observations[observation_id]
        if self.evidence_vault is not None:
            try:
                return self.evidence_vault.load_observation(observation_id)
            except FileNotFoundError:
                pass
        if self.rethinkdb_backend is not None:
            return self.rethinkdb_backend.load_observation(observation_id)
        return None


class SwarmEndpointApp:
    """In-process implementation of the planned internal swarm endpoints."""

    def __init__(self, queen: QueenCoordinator | None = None) -> None:
        self.queen = queen or QueenCoordinator()

    def get_swarm_status(self) -> dict[str, object]:
        return self.queen.status()

    def post_node_heartbeat(self, payload: Mapping[str, object]) -> dict[str, object]:
        node_id = str(payload.get("node_id", "unknown"))
        status = payload.get("status") if isinstance(payload.get("status"), Mapping) else payload
        return self.queen.heartbeat(node_id, status)

    def post_observation(self, payload: Mapping[str, object]) -> dict[str, object]:
        return self.queen.ingest_observation(ObservationPacket.from_mapping(payload))

    def get_pheromone_map(self) -> dict[str, object]:
        return self.queen.pheromone_map.as_geojson()

    def post_queen_task_hints(self, payload: Mapping[str, object] | None = None) -> dict[str, object]:
        limit = int((payload or {}).get("limit", 5))
        return {"task_hints": self.queen.pheromone_map.task_hints(limit=limit), "actuation_allowed": False}

    def post_review_packet(self, payload: Mapping[str, object]) -> dict[str, object]:
        observation_id = str(payload.get("observation_id", ""))
        observation = self.queen.find_observation(observation_id)
        if observation is None:
            raise FileNotFoundError(f"observation not found: {observation_id}")
        return SwarmReviewPacketBuilder().build(observation)


class MissionSafetyGate:
    REQUIRED_FOR_FUTURE_ACTUATION = (
        "simulation_passed",
        "geofence_id",
        "human_pilot_approval",
        "legal_authorization",
        "land_permission",
    )

    def evaluate(self, mission: Mapping[str, object]) -> dict[str, object]:
        missing = [key for key in self.REQUIRED_FOR_FUTURE_ACTUATION if not mission.get(key)]
        return {
            "actuation_allowed": False,
            "v1_policy": "passive_observation_only",
            "future_actuation_prerequisites_present": not missing,
            "missing_prerequisites": missing,
            "human_review_required": True,
            "legal_and_ecological_review_required": True,
            "ctn_boundary": "contextual trust can quarantine or flag data but cannot command flight in v1",
        }


class SwarmReviewPacketBuilder:
    def build(self, observation: ObservationPacket) -> dict[str, object]:
        domains = set(observation.lexicon_domains)
        if LexiconDomain.ARCHAEOLOGY.value in domains:
            expert_review = "archaeologist_or_heritage_authority"
        elif LexiconDomain.BIOLOGY.value in domains:
            expert_review = "field_biologist_taxonomist_or_conservation_authority"
        else:
            expert_review = "domain_specialist"
        return {
            "packet_type": "synthia_swarm_field_review_packet",
            "observation": observation.as_dict(public_safe=True),
            "expert_review_required": expert_review,
            "candidate_language_only": True,
            "sensitive_location_policy": "public packets round coordinates; private evidence may preserve exact coordinates under permission controls",
            "ai_role": "passive detection, lexicon organization, and source-linked triage only",
            "human_authority_boundary": "Synthia does not declare new species, archaeological discoveries, hazards, or conservation actions.",
            "hierarchy": HIERARCHY,
        }


def parse_detection_arg(values: Iterable[str]) -> list[dict[str, object]]:
    detections = []
    for value in values:
        if ":" in value:
            label, confidence = value.split(":", 1)
            detections.append({"label": label, "confidence": float(confidence), "source": "cli"})
        else:
            detections.append({"label": value, "confidence": 0.5, "source": "cli"})
    return detections


def load_json_mapping(value: str) -> dict[str, object]:
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)
