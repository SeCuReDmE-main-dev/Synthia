"""Research-object provenance guardrails for bounded Synthia review outputs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from .plithogenic import TIF, clamp01
from .safety import HIERARCHY


PROV_O_SOURCE_ID = "standard.w3c_prov_o"
RO_CRATE_SOURCE_ID = "standard.ro_crate"
DATACITE_SOURCE_ID = "standard.datacite_metadata_schema"
CFF_SOURCE_ID = "standard.citation_file_format"
CREDIT_SOURCE_ID = "standard.credit_taxonomy"
ACADEMIA_UPLOAD_SOURCE_ID = "platform.academia_upload_format"
ACADEMIA_COPYRIGHT_SOURCE_ID = "platform.academia_self_archiving_rights"
MIT_DSPACE_SOURCE_ID = "repository.mit_open_scholarship_dspace"
HARVARD_DASH_SOURCE_ID = "repository.harvard_dash"
CROSSREF_SOURCE_ID = "registry.crossref_rest_api"


class PlatformType(str, Enum):
    FREE_ACADEMIC_NETWORK = "free_academic_network"
    INSTITUTIONAL_REPOSITORY = "institutional_repository"
    JOURNAL_OR_SERIES_SITE = "journal_or_series_site"
    DOI_METADATA_REGISTRY = "doi_metadata_registry"
    UNKNOWN = "unknown"


class ProvenanceStatus(str, Enum):
    UNVERIFIED_CLAIM = "unverified_claim"
    PLATFORM_POSTED = "platform_posted"
    REPOSITORY_DEPOSITED = "repository_deposited"
    DOI_METADATA_LINKED = "doi_metadata_linked"
    PUBLISHER_OR_REGISTRY_VERIFIED = "publisher_or_registry_verified"


class VerificationPriority(str, Enum):
    ROUTINE = "routine"
    WATCH = "watch"
    ELEVATED = "elevated"
    CRITICAL_REVIEW = "critical_review"


class ManuscriptVersionState(str, Enum):
    UNKNOWN = "unknown"
    PREPRINT = "preprint"
    POSTPRINT = "postprint"
    PUBLISHER_VERSION = "publisher_version"
    REPOSITORY_RECORD = "repository_record"


_CREDIT_ROLES = {
    "conceptualization",
    "data_curation",
    "formal_analysis",
    "funding_acquisition",
    "investigation",
    "methodology",
    "project_administration",
    "resources",
    "software",
    "supervision",
    "validation",
    "visualization",
    "writing_original_draft",
    "writing_review_editing",
}


@dataclass(frozen=True)
class ResearchSourceEvidence:
    source_id: str
    url: str
    platform_type: str
    title: str
    claim_type: str
    T: float
    I: float
    F: float
    weight: float = 1.0
    metadata_fields: Mapping[str, object] | None = None
    rights_notes: str = ""
    source_ids: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: object, index: int) -> "ResearchSourceEvidence":
        if not isinstance(raw, Mapping):
            raise ValueError("each research source evidence record must be a JSON object")
        metadata_fields = raw.get("metadata_fields", {})
        if not isinstance(metadata_fields, Mapping):
            raise ValueError("research source evidence metadata_fields must be a JSON object")
        return cls(
            source_id=str(raw.get("source_id", f"research_source_{index + 1}")),
            url=str(raw.get("url", "")),
            platform_type=str(raw.get("platform_type", PlatformType.UNKNOWN.value)),
            title=str(raw.get("title", f"Research source evidence {index + 1}")),
            claim_type=str(raw.get("claim_type", "source_visibility")),
            T=float(raw.get("T", 0.0)),
            I=float(raw.get("I", 0.0)),
            F=float(raw.get("F", 0.0)),
            weight=max(0.0, float(raw.get("weight", 1.0))),
            metadata_fields=metadata_fields,
            rights_notes=str(raw.get("rights_notes", "")),
            source_ids=_source_ids(raw.get("source_ids", ())),
            notes=str(raw.get("notes", "")),
        )

    def operational_tif(self) -> TIF:
        return TIF(T=clamp01(self.T), I=clamp01(self.I), F=clamp01(self.F))

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "platform_type": self.platform_type,
            "title": self.title,
            "claim_type": self.claim_type,
            "formal_value": {"T": self.T, "I": self.I, "F": self.F},
            "operational_tif": self.operational_tif().as_dict(),
            "weight": self.weight,
            "metadata_fields": dict(self.metadata_fields or {}),
            "rights_notes": self.rights_notes,
            "source_ids": list(self.source_ids),
            "notes": self.notes,
        }


@dataclass(frozen=True)
class ResearchObjectProvenanceCase:
    case_label: str
    review_subject: str
    evidence_records: tuple[ResearchSourceEvidence, ...]
    source_ids: tuple[str, ...] = ()
    reviewer_notes: str = ""
    related_governance_case: Mapping[str, object] | None = None
    related_taxon_packet: Mapping[str, object] | None = None
    related_algorithm_behavior: Mapping[str, object] | None = None

    @classmethod
    def from_raw_case(cls, raw: object) -> "ResearchObjectProvenanceCase":
        if not isinstance(raw, Mapping):
            raise ValueError("research object provenance case must be a JSON object")
        evidence_records = raw.get("evidence_records", [])
        if not isinstance(evidence_records, list):
            raise ValueError("research object provenance case evidence_records must be a JSON array")
        return cls(
            case_label=str(raw.get("case_label", "unnamed research object provenance case")),
            review_subject=str(raw.get("review_subject", "")),
            evidence_records=tuple(
                ResearchSourceEvidence.from_raw(item, index) for index, item in enumerate(evidence_records)
            ),
            source_ids=_source_ids(raw.get("source_ids", ())),
            reviewer_notes=str(raw.get("reviewer_notes", "")),
            related_governance_case=_optional_mapping(raw.get("related_governance_case"), "related_governance_case"),
            related_taxon_packet=_optional_mapping(raw.get("related_taxon_packet"), "related_taxon_packet"),
            related_algorithm_behavior=_optional_mapping(
                raw.get("related_algorithm_behavior"), "related_algorithm_behavior"
            ),
        )


class ResearchObjectProvenanceReviewer:
    def score(self, case: ResearchObjectProvenanceCase | object) -> dict[str, object]:
        review_case = (
            case if isinstance(case, ResearchObjectProvenanceCase) else ResearchObjectProvenanceCase.from_raw_case(case)
        )
        if not review_case.evidence_records:
            operational_tif = TIF(T=0.0, I=1.0, F=0.0, I_system=1.0, H_lex=1.0, G_lex=1.0, I_lexicon=1.0)
            return _base_payload(
                review_case,
                operational_tif=operational_tif,
                provenance_status=ProvenanceStatus.UNVERIFIED_CLAIM.value,
                research_object_readiness=0.0,
                platform_risk_load=1.0,
                metadata_gap_load=1.0,
                rights_uncertainty_load=1.0,
                contribution_role_load=1.0,
                contradiction_load=1.0,
                uncertainty_load=1.0,
                verification_priority=VerificationPriority.CRITICAL_REVIEW.value,
            )

        weighted_tif = _weighted_tif(review_case.evidence_records)
        provenance_status = build_publication_chain_status(review_case.evidence_records)
        research_object_readiness = _research_object_readiness(review_case.evidence_records)
        platform_risk_load = _weighted_metric(review_case.evidence_records, _record_platform_risk)
        metadata_gap_load = _weighted_metric(review_case.evidence_records, _record_metadata_gap)
        rights_uncertainty_load = _weighted_metric(review_case.evidence_records, _record_rights_uncertainty)
        contribution_role_load = score_contribution_role_load(
            _collect_metadata_list(review_case.evidence_records, "contributor_roles")
        )
        contradiction_load = _contradiction_load(review_case.evidence_records, provenance_status)
        uncertainty_load = clamp01(
            max(
                weighted_tif.I,
                platform_risk_load,
                metadata_gap_load,
                rights_uncertainty_load,
                contribution_role_load,
                contradiction_load,
            )
        )
        operational_tif = TIF(
            T=weighted_tif.T,
            I=weighted_tif.I,
            F=weighted_tif.F,
            I_system=uncertainty_load,
            H_lex=metadata_gap_load,
            G_lex=contradiction_load,
            I_lexicon=uncertainty_load,
        )
        return _base_payload(
            review_case,
            operational_tif=operational_tif,
            provenance_status=provenance_status,
            research_object_readiness=research_object_readiness,
            platform_risk_load=platform_risk_load,
            metadata_gap_load=metadata_gap_load,
            rights_uncertainty_load=rights_uncertainty_load,
            contribution_role_load=contribution_role_load,
            contradiction_load=contradiction_load,
            uncertainty_load=uncertainty_load,
            verification_priority=_verification_priority(max(uncertainty_load, contradiction_load)),
        )


def score_research_object_provenance_case(raw: object) -> dict[str, object]:
    return ResearchObjectProvenanceReviewer().score(raw)


def build_prov_entity(
    entity_id: str,
    label: str,
    entity_type: str = "source_record",
    identifier: str = "",
    source_ids: Iterable[str] = (),
) -> dict[str, object]:
    return {
        "id": entity_id,
        "label": label,
        "prov_type": "Entity",
        "entity_type": entity_type,
        "identifier": identifier,
        "source_ids": list(_source_ids(source_ids)),
    }


def build_prov_activity(
    activity_id: str,
    label: str,
    activity_type: str = "review",
    used_entity_ids: Iterable[str] = (),
    generated_entity_ids: Iterable[str] = (),
    source_ids: Iterable[str] = (),
) -> dict[str, object]:
    return {
        "id": activity_id,
        "label": label,
        "prov_type": "Activity",
        "activity_type": activity_type,
        "used_entity_ids": list(_source_ids(used_entity_ids)),
        "generated_entity_ids": list(_source_ids(generated_entity_ids)),
        "source_ids": list(_source_ids(source_ids)),
    }


def build_prov_agent(
    agent_id: str,
    label: str,
    agent_type: str = "human_reviewer",
    identifier: str = "",
    source_ids: Iterable[str] = (),
) -> dict[str, object]:
    return {
        "id": agent_id,
        "label": label,
        "prov_type": "Agent",
        "agent_type": agent_type,
        "identifier": identifier,
        "source_ids": list(_source_ids(source_ids)),
    }


def link_prov_derivation(
    entity_id: str,
    source_entity_id: str,
    activity_id: str = "",
    agent_id: str = "",
    primary_source_id: str = "",
) -> dict[str, object]:
    return {
        "entity_id": entity_id,
        "wasDerivedFrom": source_entity_id,
        "wasGeneratedBy": activity_id,
        "wasAttributedTo": agent_id,
        "hadPrimarySource": primary_source_id or source_entity_id,
    }


def validate_minimal_prov_chain(chain: Mapping[str, object]) -> dict[str, object]:
    entities = _mapping_list(chain.get("entities"))
    activities = _mapping_list(chain.get("activities"))
    agents = _mapping_list(chain.get("agents"))
    missing = []
    if not entities:
        missing.append("entity")
    if not activities:
        missing.append("activity")
    if not agents:
        missing.append("agent")
    return {
        "complete": not missing,
        "missing": missing,
        "metadata_gap_load": clamp01(len(missing) / 3.0),
    }


def build_ro_crate_root(name: str, description: str = "", source_ids: Iterable[str] = ()) -> dict[str, object]:
    return {
        "@id": "./",
        "@type": "Dataset",
        "name": name,
        "description": description,
        "source_ids": list(_source_ids(source_ids)),
    }


def build_ro_crate_data_entity(entity_id: str, name: str, encoding_format: str = "", source_ids: Iterable[str] = ()) -> dict[str, object]:
    return {
        "@id": entity_id,
        "@type": "File" if encoding_format else "CreativeWork",
        "name": name,
        "encodingFormat": encoding_format,
        "source_ids": list(_source_ids(source_ids)),
    }


def build_ro_crate_contextual_entity(entity_id: str, name: str, entity_type: str = "Person", source_ids: Iterable[str] = ()) -> dict[str, object]:
    return {
        "@id": entity_id,
        "@type": entity_type,
        "name": name,
        "source_ids": list(_source_ids(source_ids)),
    }


def build_ro_crate_provenance_block(
    prov_entities: Iterable[Mapping[str, object]],
    prov_activities: Iterable[Mapping[str, object]],
    prov_agents: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    return {
        "prov_entities": [dict(entity) for entity in prov_entities],
        "prov_activities": [dict(activity) for activity in prov_activities],
        "prov_agents": [dict(agent) for agent in prov_agents],
        "minimal_chain": validate_minimal_prov_chain(
            {"entities": tuple(prov_entities), "activities": tuple(prov_activities), "agents": tuple(prov_agents)}
        ),
    }


def score_ro_crate_readiness(crate: Mapping[str, object]) -> float:
    root = crate.get("root")
    data_entities = _mapping_list(crate.get("data_entities"))
    contextual_entities = _mapping_list(crate.get("contextual_entities"))
    provenance_block = crate.get("provenance_block")
    present = sum(
        (
            isinstance(root, Mapping),
            bool(data_entities),
            bool(contextual_entities),
            isinstance(provenance_block, Mapping),
        )
    )
    return clamp01(present / 4.0)


def normalize_datacite_identifier(value: object) -> dict[str, object]:
    identifier = str(value.get("identifier", value.get("value", ""))) if isinstance(value, Mapping) else str(value or "")
    lowered = identifier.lower()
    if lowered.startswith("10."):
        identifier_type = "DOI"
    elif "handle" in lowered or "hdl.handle.net" in lowered:
        identifier_type = "Handle"
    elif lowered.startswith("http://") or lowered.startswith("https://"):
        identifier_type = "URL"
    elif identifier:
        identifier_type = "Accession"
    else:
        identifier_type = "Unknown"
    return {"identifier": identifier, "identifier_type": identifier_type, "present": bool(identifier)}


def normalize_datacite_creators(value: object) -> list[dict[str, object]]:
    creators = value if isinstance(value, list) else [value] if value else []
    normalized = []
    for index, creator in enumerate(creators):
        if isinstance(creator, Mapping):
            normalized.append(
                {
                    "name": str(creator.get("name", "")),
                    "orcid": str(creator.get("orcid", "")),
                    "affiliation": str(creator.get("affiliation", "")),
                    "creator_order": int(creator.get("creator_order", index + 1)),
                }
            )
        else:
            normalized.append({"name": str(creator), "orcid": "", "affiliation": "", "creator_order": index + 1})
    return normalized


def normalize_datacite_resource_type(value: object) -> str:
    normalized = str(value or "unknown").strip().lower().replace("-", "_").replace(" ", "_")
    allowed = {"article", "preprint", "dataset", "software", "report", "book", "thesis", "white_paper"}
    return normalized if normalized in allowed else "unknown"


def normalize_datacite_related_identifiers(value: object) -> list[dict[str, object]]:
    relations = value if isinstance(value, list) else [value] if value else []
    normalized = []
    for relation in relations:
        if isinstance(relation, Mapping):
            normalized.append(
                {
                    "identifier": str(relation.get("identifier", "")),
                    "relation_type": str(relation.get("relation_type", "unknown")),
                    "identifier_type": normalize_datacite_identifier(relation.get("identifier", ""))["identifier_type"],
                }
            )
    return normalized


def score_datacite_metadata_gap(metadata: Mapping[str, object]) -> float:
    required = ("identifier", "creators", "title", "publisher", "date", "version", "related_identifiers")
    missing = [field for field in required if _missing(metadata.get(field))]
    return clamp01(len(missing) / len(required))


def build_citation_cff_payload(metadata: Mapping[str, object]) -> dict[str, object]:
    return {
        "cff-version": str(metadata.get("cff-version", "1.2.0")),
        "message": str(metadata.get("message", "If you use this Synthia output, cite the linked source package.")),
        "title": str(metadata.get("title", "")),
        "authors": normalize_datacite_creators(metadata.get("authors", metadata.get("creators", []))),
        "version": str(metadata.get("version", "")),
        "date-released": str(metadata.get("date-released", metadata.get("date", ""))),
        "identifiers": metadata.get("identifiers", []),
    }


def validate_cff_required_fields(cff_payload: Mapping[str, object]) -> dict[str, object]:
    required = ("cff-version", "message", "title", "authors", "version", "date-released", "identifiers")
    missing = [field for field in required if _missing(cff_payload.get(field))]
    return {"valid": not missing, "missing": missing, "metadata_gap_load": clamp01(len(missing) / len(required))}


def build_cff_preferred_citation(software_metadata: Mapping[str, object], scientific_metadata: Mapping[str, object]) -> dict[str, object]:
    return {
        "software_citation": build_citation_cff_payload(software_metadata),
        "scientific_citation": build_citation_cff_payload(scientific_metadata),
        "boundary": "Software citation and scientific source citation remain separate.",
    }


def build_cff_references(references: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "title": str(reference.get("title", "")),
            "url": str(reference.get("url", "")),
            "source_id": str(reference.get("source_id", "")),
        }
        for reference in references
    ]


def score_cff_citation_readiness(cff_payload: Mapping[str, object]) -> float:
    return clamp01(1.0 - validate_cff_required_fields(cff_payload)["metadata_gap_load"])


def normalize_credit_role(value: object) -> str:
    text = str(value or "").strip().lower().replace("&", " ")
    for char in ("-", "/", ",", ";", ":", "(", ")", "."):
        text = text.replace(char, " ")
    role = "_".join(part for part in text.split() if part != "and")
    aliases = {
        "writing_review_editing": "writing_review_editing",
        "writing_original": "writing_original_draft",
        "writing_original_draft": "writing_original_draft",
    }
    role = aliases.get(role, role)
    return role if role in _CREDIT_ROLES else "unknown"


def map_contributor_roles(contributors: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    mapped = []
    for contributor in contributors:
        roles = contributor.get("roles", [])
        roles = roles if isinstance(roles, list) else [roles]
        mapped.append(
            {
                "name": str(contributor.get("name", "")),
                "roles": [normalize_credit_role(role) for role in roles],
                "authority_boundary": build_contribution_boundary(contributor),
            }
        )
    return mapped


def build_contribution_boundary(contributor: Mapping[str, object]) -> str:
    roles = [normalize_credit_role(role) for role in _as_list(contributor.get("roles", []))]
    if "software" in roles:
        return "Software contribution may be credited, but scientific authority still requires human review."
    if {"conceptualization", "methodology", "supervision", "validation"} & set(roles):
        return (
            "Scientific conception or review contribution may be credited; it does not create code authorship, "
            "formal nomenclatural authority, or autonomous Synthia authority."
        )
    return "Contributor role is descriptive provenance only."


def score_contribution_role_load(contributors: Iterable[object]) -> float:
    contributors = tuple(contributors)
    if not contributors:
        return 1.0
    unknown = 0
    total = 0
    for contributor in contributors:
        if isinstance(contributor, Mapping):
            roles = _as_list(contributor.get("roles", []))
        else:
            roles = [contributor]
        if not roles:
            unknown += 1
            total += 1
        for role in roles:
            total += 1
            if normalize_credit_role(role) == "unknown":
                unknown += 1
    return clamp01(unknown / (total or 1))


def render_public_contributor_summary(contributors: Iterable[Mapping[str, object]]) -> str:
    parts = []
    for contributor in map_contributor_roles(contributors):
        roles = ", ".join(role for role in contributor["roles"] if role != "unknown") or "role pending review"
        parts.append(f"{contributor['name']}: {roles}")
    return "; ".join(parts)


def classify_academia_upload_record(record: Mapping[str, object]) -> str:
    return PlatformType.FREE_ACADEMIC_NETWORK.value


def extract_academia_post_metadata(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "title": str(record.get("title", "")),
        "abstract": str(record.get("abstract", "")),
        "co_authors": list(_as_list(record.get("co_authors", []))),
        "research_interests": list(_as_list(record.get("research_interests", record.get("tags", [])))),
        "file_present": bool(record.get("file_present", False)),
        "summary_text_present": bool(record.get("summary_text", "")),
        "post_url": str(record.get("post_url", record.get("url", ""))),
    }


def score_academia_metadata_completeness(record: Mapping[str, object]) -> float:
    metadata = extract_academia_post_metadata(record)
    required = ("title", "abstract", "co_authors", "research_interests", "post_url")
    present = sum(not _missing(metadata.get(field)) for field in required)
    if metadata["file_present"]:
        present += 1
    return clamp01(present / (len(required) + 1))


def detect_academia_fileless_or_general_post(record: Mapping[str, object]) -> bool:
    kind = str(record.get("document_type", record.get("claim_type", ""))).lower()
    return not bool(record.get("file_present", False)) or kind in {"poem", "citation", "book", "general_post", "post"}


def score_free_platform_risk(record: Mapping[str, object], cross_verified: bool = False) -> float:
    base = 0.85 if classify_academia_upload_record(record) == PlatformType.FREE_ACADEMIC_NETWORK.value else 0.5
    if cross_verified:
        base -= 0.45
    if detect_academia_fileless_or_general_post(record):
        base += 0.10
    return clamp01(base)


def classify_manuscript_version_state(value: object) -> str:
    normalized = str(value or "unknown").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"post_print": "postprint", "pre_print": "preprint", "publisher_pdf": "publisher_version"}
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in {state.value for state in ManuscriptVersionState} else ManuscriptVersionState.UNKNOWN.value


def extract_self_archiving_rights_signal(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "publisher_agreement_present": bool(record.get("publisher_agreement")),
        "embargo": str(record.get("embargo", "")),
        "license_note": str(record.get("license_note", "")),
        "rights_note": str(record.get("rights_note", record.get("rights_notes", ""))),
        "rights_known": bool(record.get("publisher_agreement") or record.get("license_note") or record.get("rights_note")),
    }


def score_rights_uncertainty(record: Mapping[str, object]) -> float:
    rights = extract_self_archiving_rights_signal(record)
    version_state = classify_manuscript_version_state(record.get("version_state"))
    uncertainty = 0.35
    if not rights["rights_known"]:
        uncertainty += 0.45
    if version_state == ManuscriptVersionState.UNKNOWN.value:
        uncertainty += 0.20
    return clamp01(uncertainty)


def separate_accessibility_from_validity(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "accessible_online": bool(record.get("url") or record.get("file_present")),
        "scientifically_validated": False,
        "boundary": "Online accessibility is not scientific validation.",
    }


def build_copyright_review_warning(record: Mapping[str, object]) -> str:
    if score_rights_uncertainty(record) >= 0.60:
        return "Rights or version state is unclear; human review is required before reuse or publication."
    return "Rights signal is present, but human review remains required."


def classify_institutional_repository_record(record: Mapping[str, object]) -> str:
    return PlatformType.INSTITUTIONAL_REPOSITORY.value


def extract_repository_structure(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "community": str(record.get("community", "")),
        "collection": str(record.get("collection", "")),
        "item_url": str(record.get("item_url", record.get("url", ""))),
        "persistent_url": str(record.get("persistent_url", record.get("handle", ""))),
        "depositor_scope": str(record.get("depositor_scope", "")),
        "content_type": str(record.get("content_type", "")),
    }


def score_repository_preservation_signal(record: Mapping[str, object]) -> float:
    signals = (
        bool(record.get("institutional_host")),
        bool(record.get("persistent_url") or record.get("handle")),
        bool(record.get("preservation_signal")),
        bool(record.get("indexing_signal")),
    )
    return clamp01(sum(signals) / len(signals))


def separate_repository_deposit_from_peer_review(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "repository_deposited": True,
        "peer_review_verified": bool(record.get("peer_review_verified", False)),
        "boundary": "Repository deposit improves provenance but does not prove peer review.",
    }


def map_repository_to_research_object_entity(record: Mapping[str, object]) -> dict[str, object]:
    structure = extract_repository_structure(record)
    return build_ro_crate_data_entity(
        structure["persistent_url"] or structure["item_url"] or str(record.get("source_id", "repository_record")),
        str(record.get("title", "Repository record")),
        source_ids=_source_ids(record.get("source_ids", ())),
    )


def classify_dash_open_access_record(record: Mapping[str, object]) -> str:
    return PlatformType.INSTITUTIONAL_REPOSITORY.value


def extract_dash_discoverability_signals(record: Mapping[str, object]) -> dict[str, object]:
    return {
        "search_supported": bool(record.get("search_supported", True)),
        "browse_fields": list(_as_list(record.get("browse_fields", []))),
        "google_scholar_indexing": bool(record.get("google_scholar_indexing", False)),
        "catalog_visibility": bool(record.get("catalog_visibility", False)),
    }


def score_dash_persistent_access_signal(record: Mapping[str, object]) -> float:
    signals = (
        bool(record.get("persistent_url")),
        bool(record.get("preservation_signal")),
        bool(record.get("license_note") or record.get("copyright_note")),
        bool(record.get("open_download")),
    )
    return clamp01(sum(signals) / len(signals))


def detect_early_version_priority_signal(record: Mapping[str, object]) -> bool:
    version_state = classify_manuscript_version_state(record.get("version_state"))
    return version_state in {ManuscriptVersionState.PREPRINT.value, ManuscriptVersionState.UNKNOWN.value}


def compare_repository_vs_free_platform(repository_record: Mapping[str, object], free_platform_record: Mapping[str, object]) -> dict[str, object]:
    repository_risk = clamp01(0.55 - (0.35 * score_repository_preservation_signal(repository_record)))
    free_platform_risk = score_free_platform_risk(free_platform_record)
    return {
        "repository_platform_risk": repository_risk,
        "free_platform_risk": free_platform_risk,
        "repository_lowers_risk": repository_risk < free_platform_risk,
    }


def normalize_crossref_work_metadata(metadata: Mapping[str, object]) -> dict[str, object]:
    return {
        "doi": str(metadata.get("doi", metadata.get("DOI", ""))),
        "title": str(metadata.get("title", "")),
        "publisher": str(metadata.get("publisher", metadata.get("member", ""))),
        "type": str(metadata.get("type", "")),
        "date": str(metadata.get("date", metadata.get("issued", ""))),
        "author": normalize_datacite_creators(metadata.get("author", metadata.get("authors", []))),
        "license": metadata.get("license", ""),
        "funder": metadata.get("funder", ""),
        "references": list(_as_list(metadata.get("references", []))),
        "relations": list(_as_list(metadata.get("relations", []))),
        "orcid": str(metadata.get("orcid", "")),
        "ror": str(metadata.get("ror", "")),
    }


def score_crossref_registry_verification(metadata: Mapping[str, object]) -> float:
    normalized = normalize_crossref_work_metadata(metadata)
    signals = (
        bool(normalized["doi"]),
        bool(normalized["title"]),
        bool(normalized["publisher"]),
        bool(normalized["date"]),
        bool(normalized["type"]),
    )
    return clamp01(sum(signals) / len(signals))


def detect_crossref_relation_chain(metadata: Mapping[str, object]) -> dict[str, object]:
    normalized = normalize_crossref_work_metadata(metadata)
    relations = normalized["relations"]
    references = normalized["references"]
    return {
        "has_relations": bool(relations),
        "has_references": bool(references),
        "relation_count": len(relations),
        "reference_count": len(references),
        "chain_present": bool(relations or references),
    }


def compare_claim_against_registry_metadata(claim: Mapping[str, object], registry_metadata: Mapping[str, object]) -> float:
    registry = normalize_crossref_work_metadata(registry_metadata)
    compared = 0
    mismatches = 0
    for field in ("title", "date", "publisher"):
        claim_value = str(claim.get(field, "")).strip().lower()
        registry_value = str(registry.get(field, "")).strip().lower()
        if claim_value and registry_value:
            compared += 1
            if claim_value != registry_value:
                mismatches += 1
    claim_authors = {str(author).strip().lower() for author in _as_list(claim.get("authors", [])) if str(author)}
    registry_authors = {str(author.get("name", "")).strip().lower() for author in registry["author"] if author.get("name")}
    if claim_authors and registry_authors:
        compared += 1
        if not claim_authors & registry_authors:
            mismatches += 1
    return clamp01(mismatches / (compared or 1))


def build_publication_chain_status(records: Iterable[ResearchSourceEvidence] | Iterable[Mapping[str, object]]) -> str:
    statuses = {_record_status(record) for record in records}
    order = (
        ProvenanceStatus.PUBLISHER_OR_REGISTRY_VERIFIED.value,
        ProvenanceStatus.DOI_METADATA_LINKED.value,
        ProvenanceStatus.REPOSITORY_DEPOSITED.value,
        ProvenanceStatus.PLATFORM_POSTED.value,
        ProvenanceStatus.UNVERIFIED_CLAIM.value,
    )
    for status in order:
        if status in statuses:
            return status
    return ProvenanceStatus.UNVERIFIED_CLAIM.value


def build_academic_platform_demo_case() -> ResearchObjectProvenanceCase:
    source_ids = (
        PROV_O_SOURCE_ID,
        RO_CRATE_SOURCE_ID,
        DATACITE_SOURCE_ID,
        CFF_SOURCE_ID,
        CREDIT_SOURCE_ID,
        ACADEMIA_UPLOAD_SOURCE_ID,
        ACADEMIA_COPYRIGHT_SOURCE_ID,
        MIT_DSPACE_SOURCE_ID,
        HARVARD_DASH_SOURCE_ID,
        CROSSREF_SOURCE_ID,
    )
    return ResearchObjectProvenanceCase(
        case_label="Synthetic academic platform provenance case",
        review_subject="Synthia source verification and research-object export packet",
        source_ids=source_ids,
        evidence_records=(
            ResearchSourceEvidence(
                source_id=ACADEMIA_UPLOAD_SOURCE_ID,
                url="https://support.academia.edu/hc/en-us/articles/360043383793-How-to-upload-a-document-to-Academia",
                platform_type=PlatformType.FREE_ACADEMIC_NETWORK.value,
                title="Academia upload-format signal",
                claim_type="platform_visibility",
                T=0.58,
                I=0.34,
                F=0.12,
                weight=0.8,
                metadata_fields={
                    "title": "Synthetic public profile post",
                    "abstract": "Synthetic summary only",
                    "co_authors": ["Synthetic reviewer"],
                    "research_interests": ["taxonomy", "provenance"],
                    "file_present": True,
                    "version_state": "preprint",
                    "rights_note": "Synthetic public-safe example; reuse still requires human review.",
                    "contributor_roles": [{"name": "Synthetic reviewer", "roles": ["validation"]}],
                },
                rights_notes="Synthetic public-safe example; reuse still requires human review.",
                source_ids=(ACADEMIA_UPLOAD_SOURCE_ID,),
                notes="Free-platform visibility is not publication-chain verification.",
            ),
            ResearchSourceEvidence(
                source_id=MIT_DSPACE_SOURCE_ID,
                url="https://libguides.mit.edu/dspace",
                platform_type=PlatformType.INSTITUTIONAL_REPOSITORY.value,
                title="Institutional repository signal",
                claim_type="repository_deposit",
                T=0.78,
                I=0.20,
                F=0.06,
                weight=1.0,
                metadata_fields={
                    "identifier": "https://example.test/handle/synthetic",
                    "creators": ["Synthetic author"],
                    "title": "Synthetic repository item",
                    "publisher": "Synthetic institution",
                    "date": "2026",
                    "version": "repository_record",
                    "version_state": "repository_record",
                    "rights_note": "Synthetic repository rights note.",
                    "related_identifiers": ["10.0000/synthetic"],
                    "institutional_host": True,
                    "persistent_url": "https://example.test/handle/synthetic",
                    "preservation_signal": True,
                    "indexing_signal": True,
                },
                rights_notes="Synthetic repository rights note.",
                source_ids=(MIT_DSPACE_SOURCE_ID, RO_CRATE_SOURCE_ID, DATACITE_SOURCE_ID),
                notes="Repository deposit improves provenance while preserving review boundaries.",
            ),
            ResearchSourceEvidence(
                source_id=CROSSREF_SOURCE_ID,
                url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
                platform_type=PlatformType.DOI_METADATA_REGISTRY.value,
                title="Registry metadata signal",
                claim_type="doi_metadata",
                T=0.84,
                I=0.14,
                F=0.05,
                weight=1.2,
                metadata_fields={
                    "doi": "10.0000/synthetic",
                    "title": "Synthetic repository item",
                    "publisher": "Synthetic publisher",
                    "date": "2026",
                    "type": "report",
                    "version_state": "publisher_version",
                    "rights_note": "Synthetic registry rights metadata.",
                    "author": [{"name": "Synthetic author"}],
                    "relations": [{"relation_type": "isVersionOf", "identifier": "https://example.test/source"}],
                    "contributor_roles": [
                        {"name": "Jean-Sebastien Beaulieu", "roles": ["software", "methodology"]},
                        {"name": "Prof. Hector Fernando Aguilar", "roles": ["conceptualization", "validation"]},
                    ],
                },
                rights_notes="Synthetic registry rights metadata.",
                source_ids=(CROSSREF_SOURCE_ID, CFF_SOURCE_ID, CREDIT_SOURCE_ID, PROV_O_SOURCE_ID),
                notes="Synthetic registry metadata; no scientific truth certification.",
            ),
        ),
        reviewer_notes="Public-safe synthetic demo; no live scraping or private source text.",
        related_governance_case={"case_label": "Synthetic governance case", "human_review_required": True},
    )


def _base_payload(
    case: ResearchObjectProvenanceCase,
    operational_tif: TIF,
    provenance_status: str,
    research_object_readiness: float,
    platform_risk_load: float,
    metadata_gap_load: float,
    rights_uncertainty_load: float,
    contribution_role_load: float,
    contradiction_load: float,
    uncertainty_load: float,
    verification_priority: str,
) -> dict[str, object]:
    return {
        "case_label": case.case_label,
        "review_subject": case.review_subject,
        "evidence_records": [record.as_dict() for record in case.evidence_records],
        "source_ids": list(_all_source_ids(case)),
        "provenance_status": provenance_status,
        "research_object_readiness": research_object_readiness,
        "platform_risk_load": platform_risk_load,
        "metadata_gap_load": metadata_gap_load,
        "rights_uncertainty_load": rights_uncertainty_load,
        "contribution_role_load": contribution_role_load,
        "contradiction_load": contradiction_load,
        "uncertainty_load": uncertainty_load,
        "verification_priority": verification_priority,
        "operational_tif": operational_tif.as_dict(),
        "provenance_graph_hint": _provenance_graph_hint(case),
        "research_object_manifest_hint": _research_object_manifest_hint(case),
        "citation_metadata_hint": _citation_metadata_hint(case),
        "contributor_role_hint": _contributor_role_hint(case),
        "related_governance_case": case.related_governance_case,
        "related_taxon_packet": case.related_taxon_packet,
        "related_algorithm_behavior": case.related_algorithm_behavior,
        "reviewer_notes": case.reviewer_notes,
        "human_review_required": True,
        "authority_boundary": (
            "Review support only; no scientific certification, no formal taxonomic act, no legal reuse decision, "
            "no safety declaration, no diagnostic result, and no autonomous conclusion."
        ),
        "scientific_boundary": (
            "Platform visibility, repository deposit, DOI metadata, citation metadata, and contributor roles are "
            "provenance evidence classes; they are not proof of scientific truth."
        ),
        "hierarchy": HIERARCHY,
    }


def _provenance_graph_hint(case: ResearchObjectProvenanceCase) -> dict[str, object]:
    entity = build_prov_entity("entity.review_subject", case.review_subject or case.case_label, "review_packet", source_ids=case.source_ids)
    activity = build_prov_activity("activity.synthia_review", "Synthia provenance scoring", "scoring", used_entity_ids=(entity["id"],), source_ids=case.source_ids)
    agent = build_prov_agent("agent.synthia", "Synthia", "software_agent", source_ids=(PROV_O_SOURCE_ID,))
    return build_ro_crate_provenance_block((entity,), (activity,), (agent,))


def _research_object_manifest_hint(case: ResearchObjectProvenanceCase) -> dict[str, object]:
    root = build_ro_crate_root(case.case_label, "Synthia research-object provenance review packet", source_ids=case.source_ids)
    data_entities = [
        build_ro_crate_data_entity(record.source_id, record.title, source_ids=record.source_ids) for record in case.evidence_records
    ]
    contextual_entities = [
        build_ro_crate_contextual_entity("context.human_review", "Human specialist review", "Role", source_ids=(RO_CRATE_SOURCE_ID,))
    ]
    provenance = _provenance_graph_hint(case)
    return {
        "root": root,
        "data_entities": data_entities,
        "contextual_entities": contextual_entities,
        "provenance_block": provenance,
        "readiness": score_ro_crate_readiness(
            {
                "root": root,
                "data_entities": data_entities,
                "contextual_entities": contextual_entities,
                "provenance_block": provenance,
            }
        ),
    }


def _citation_metadata_hint(case: ResearchObjectProvenanceCase) -> dict[str, object]:
    metadata = _best_metadata(case.evidence_records)
    cff = build_citation_cff_payload(
        {
            "title": case.review_subject or case.case_label,
            "creators": metadata.get("creators", metadata.get("author", [])),
            "version": metadata.get("version", "pending-review"),
            "date": metadata.get("date", ""),
            "identifiers": [normalize_datacite_identifier(metadata.get("identifier", metadata.get("doi", "")))],
        }
    )
    return {
        "datacite_identifier": normalize_datacite_identifier(metadata.get("identifier", metadata.get("doi", ""))),
        "datacite_resource_type": normalize_datacite_resource_type(metadata.get("resource_type", metadata.get("type", ""))),
        "datacite_metadata_gap": score_datacite_metadata_gap(metadata),
        "cff_payload": cff,
        "cff_readiness": score_cff_citation_readiness(cff),
    }


def _contributor_role_hint(case: ResearchObjectProvenanceCase) -> dict[str, object]:
    contributors = _collect_metadata_list(case.evidence_records, "contributor_roles")
    mapped = map_contributor_roles(tuple(contributor for contributor in contributors if isinstance(contributor, Mapping)))
    return {
        "mapped_roles": mapped,
        "role_load": score_contribution_role_load(contributors),
        "public_summary": render_public_contributor_summary(tuple(contributor for contributor in contributors if isinstance(contributor, Mapping))),
    }


def _source_ids(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value)
    return (str(value),)


def _optional_mapping(value: object, label: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object when provided")
    return value


def _weighted_tif(records: Iterable[ResearchSourceEvidence]) -> TIF:
    records = tuple(records)
    if not records:
        return TIF(T=0.0, I=1.0, F=0.0)
    weight_sum = sum(record.weight for record in records) or 1.0
    return TIF(
        T=clamp01(sum(record.operational_tif().T * record.weight for record in records) / weight_sum),
        I=clamp01(sum(record.operational_tif().I * record.weight for record in records) / weight_sum),
        F=clamp01(sum(record.operational_tif().F * record.weight for record in records) / weight_sum),
    )


def _weighted_metric(records: Iterable[ResearchSourceEvidence], metric) -> float:
    records = tuple(records)
    if not records:
        return 1.0
    weight_sum = sum(record.weight for record in records) or 1.0
    return clamp01(sum(metric(record) * record.weight for record in records) / weight_sum)


def _research_object_readiness(records: Iterable[ResearchSourceEvidence]) -> float:
    records = tuple(records)
    if not records:
        return 0.0
    metadata_readiness = 1.0 - _weighted_metric(records, _record_metadata_gap)
    platform_signal = 1.0 - _weighted_metric(records, _record_platform_risk)
    return clamp01((metadata_readiness + platform_signal) / 2.0)


def _record_platform_risk(record: ResearchSourceEvidence) -> float:
    if record.platform_type == PlatformType.DOI_METADATA_REGISTRY.value:
        return clamp01(0.10 + (0.30 * _record_metadata_gap(record)))
    if record.platform_type == PlatformType.INSTITUTIONAL_REPOSITORY.value:
        return clamp01(0.45 - (0.25 * score_repository_preservation_signal(record.metadata_fields or {})))
    if record.platform_type == PlatformType.JOURNAL_OR_SERIES_SITE.value:
        return 0.35
    if record.platform_type == PlatformType.FREE_ACADEMIC_NETWORK.value:
        cross_verified = bool({"doi", "identifier", "persistent_url"} & set((record.metadata_fields or {}).keys()))
        return score_free_platform_risk(record.metadata_fields or {}, cross_verified=cross_verified)
    return 0.75


def _record_metadata_gap(record: ResearchSourceEvidence) -> float:
    metadata = record.metadata_fields or {}
    if record.platform_type == PlatformType.DOI_METADATA_REGISTRY.value:
        return clamp01(1.0 - score_crossref_registry_verification(metadata))
    if record.platform_type == PlatformType.FREE_ACADEMIC_NETWORK.value:
        return clamp01(1.0 - score_academia_metadata_completeness(metadata))
    return score_datacite_metadata_gap(metadata)


def _record_rights_uncertainty(record: ResearchSourceEvidence) -> float:
    metadata = dict(record.metadata_fields or {})
    if record.rights_notes and "rights_note" not in metadata:
        metadata["rights_note"] = record.rights_notes
    return score_rights_uncertainty(metadata)


def _contradiction_load(records: Iterable[ResearchSourceEvidence], provenance_status: str) -> float:
    records = tuple(records)
    if not records:
        return 1.0
    status_signal = {
        ProvenanceStatus.PUBLISHER_OR_REGISTRY_VERIFIED.value: 0.15,
        ProvenanceStatus.DOI_METADATA_LINKED.value: 0.25,
        ProvenanceStatus.REPOSITORY_DEPOSITED.value: 0.40,
        ProvenanceStatus.PLATFORM_POSTED.value: 0.65,
        ProvenanceStatus.UNVERIFIED_CLAIM.value: 0.85,
    }.get(provenance_status, 0.85)
    weight_sum = sum(record.weight for record in records) or 1.0
    load = 0.0
    for record in records:
        tif = record.operational_tif()
        load += max(tif.T * max(tif.I, tif.F), tif.T * status_signal * _record_metadata_gap(record)) * record.weight
    return clamp01(load / weight_sum)


def _verification_priority(signal: float) -> str:
    if signal >= 0.75:
        return VerificationPriority.CRITICAL_REVIEW.value
    if signal >= 0.50:
        return VerificationPriority.ELEVATED.value
    if signal >= 0.25:
        return VerificationPriority.WATCH.value
    return VerificationPriority.ROUTINE.value


def _record_status(record: ResearchSourceEvidence | Mapping[str, object]) -> str:
    if isinstance(record, ResearchSourceEvidence):
        platform_type = record.platform_type
        metadata = record.metadata_fields or {}
    else:
        platform_type = str(record.get("platform_type", PlatformType.UNKNOWN.value))
        metadata = record.get("metadata_fields", record)
        metadata = metadata if isinstance(metadata, Mapping) else {}
    if platform_type == PlatformType.DOI_METADATA_REGISTRY.value:
        return (
            ProvenanceStatus.PUBLISHER_OR_REGISTRY_VERIFIED.value
            if score_crossref_registry_verification(metadata) >= 0.80
            else ProvenanceStatus.DOI_METADATA_LINKED.value
        )
    if platform_type == PlatformType.INSTITUTIONAL_REPOSITORY.value:
        return ProvenanceStatus.REPOSITORY_DEPOSITED.value
    if platform_type == PlatformType.FREE_ACADEMIC_NETWORK.value:
        return ProvenanceStatus.PLATFORM_POSTED.value
    return ProvenanceStatus.UNVERIFIED_CLAIM.value


def _all_source_ids(case: ResearchObjectProvenanceCase) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for source_id in case.source_ids:
        if source_id not in seen:
            seen.add(source_id)
            ordered.append(source_id)
    for record in case.evidence_records:
        for source_id in (record.source_id, *record.source_ids):
            if source_id not in seen:
                seen.add(source_id)
                ordered.append(source_id)
    return tuple(ordered)


def _mapping_list(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, Mapping)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
        return not list(value)
    if isinstance(value, Mapping):
        return not bool(value)
    return False


def _collect_metadata_list(records: Iterable[ResearchSourceEvidence], key: str) -> list[object]:
    values: list[object] = []
    for record in records:
        value = (record.metadata_fields or {}).get(key)
        values.extend(_as_list(value))
    return values


def _best_metadata(records: Iterable[ResearchSourceEvidence]) -> Mapping[str, object]:
    records = tuple(records)
    if not records:
        return {}
    return max(records, key=lambda record: (1.0 - _record_metadata_gap(record), record.weight)).metadata_fields or {}
