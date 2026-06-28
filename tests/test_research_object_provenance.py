import json

from synthia_core.cli import main
from synthia_core.safety import HIERARCHY
import synthia_core.research_object_provenance as rop


def test_parser_preserves_source_ids_formal_values_and_bounds():
    case = rop.ResearchObjectProvenanceCase.from_raw_case(
        {
            "case_label": "Parser provenance case",
            "review_subject": "Synthetic source",
            "source_ids": ["source.case"],
            "evidence_records": [
                {
                    "source_id": "source.record",
                    "url": "https://example.test/source",
                    "platform_type": rop.PlatformType.UNKNOWN.value,
                    "title": "Synthetic source",
                    "claim_type": "source_visibility",
                    "T": 1.4,
                    "I": 0.4,
                    "F": -0.2,
                    "weight": -2.0,
                    "source_ids": ["source.inner"],
                    "metadata_fields": {"title": "Synthetic source"},
                }
            ],
        }
    )
    payload = rop.score_research_object_provenance_case(case)
    record = payload["evidence_records"][0]

    assert payload["source_ids"][:3] == ["source.case", "source.record", "source.inner"]
    assert record["formal_value"]["T"] == 1.4
    assert record["formal_value"]["F"] == -0.2
    assert record["operational_tif"]["T"] == 1.0
    assert record["operational_tif"]["F"] == 0.0
    assert record["weight"] == 0.0
    assert payload["human_review_required"] is True
    assert payload["hierarchy"] == HIERARCHY


def test_rejects_bad_case_shapes_and_related_payloads():
    try:
        rop.ResearchObjectProvenanceCase.from_raw_case([])
    except ValueError as exc:
        assert "must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object case should be rejected")

    try:
        rop.ResearchObjectProvenanceCase.from_raw_case({"evidence_records": {"bad": True}})
    except ValueError as exc:
        assert "evidence_records must be a JSON array" in str(exc)
    else:
        raise AssertionError("non-array evidence_records should be rejected")

    try:
        rop.ResearchObjectProvenanceCase.from_raw_case({"evidence_records": [], "related_taxon_packet": []})
    except ValueError as exc:
        assert "related_taxon_packet must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object related payload should be rejected")

    try:
        rop.ResearchSourceEvidence.from_raw({"metadata_fields": []}, 0)
    except ValueError as exc:
        assert "metadata_fields must be a JSON object" in str(exc)
    else:
        raise AssertionError("non-object metadata_fields should be rejected")


def test_empty_evidence_is_critical_and_bounded():
    payload = rop.score_research_object_provenance_case({"case_label": "Empty provenance", "evidence_records": []})

    assert payload["provenance_status"] == rop.ProvenanceStatus.UNVERIFIED_CLAIM.value
    assert payload["research_object_readiness"] == 0.0
    assert payload["platform_risk_load"] == 1.0
    assert payload["metadata_gap_load"] == 1.0
    assert payload["rights_uncertainty_load"] == 1.0
    assert payload["contribution_role_load"] == 1.0
    assert payload["verification_priority"] == rop.VerificationPriority.CRITICAL_REVIEW.value
    assert payload["operational_tif"]["T"] == 0.0
    assert payload["operational_tif"]["I"] == 1.0


def test_prov_o_extracted_functions_build_minimal_chain():
    entity = rop.build_prov_entity("entity.paper", "Synthetic paper", "paper", "10.0000/example")
    activity = rop.build_prov_activity("activity.review", "Review source", used_entity_ids=("entity.paper",))
    agent = rop.build_prov_agent("agent.reviewer", "Human reviewer")
    link = rop.link_prov_derivation("entity.packet", "entity.paper", "activity.review", "agent.reviewer")
    validation = rop.validate_minimal_prov_chain({"entities": [entity], "activities": [activity], "agents": [agent]})

    assert entity["prov_type"] == "Entity"
    assert activity["prov_type"] == "Activity"
    assert agent["prov_type"] == "Agent"
    assert link["hadPrimarySource"] == "entity.paper"
    assert validation["complete"] is True
    assert validation["metadata_gap_load"] == 0.0


def test_ro_crate_extracted_functions_measure_readiness():
    root = rop.build_ro_crate_root("Synthetic crate")
    data_entity = rop.build_ro_crate_data_entity("source.pdf", "Source PDF", "application/pdf")
    contextual_entity = rop.build_ro_crate_contextual_entity("person:reviewer", "Human reviewer")
    provenance = rop.build_ro_crate_provenance_block(
        [rop.build_prov_entity("entity.source", "Source")],
        [rop.build_prov_activity("activity.ingest", "Ingest")],
        [rop.build_prov_agent("agent.synthia", "Synthia", "software_agent")],
    )
    readiness = rop.score_ro_crate_readiness(
        {
            "root": root,
            "data_entities": [data_entity],
            "contextual_entities": [contextual_entity],
            "provenance_block": provenance,
        }
    )

    assert root["@type"] == "Dataset"
    assert data_entity["@type"] == "File"
    assert contextual_entity["@type"] == "Person"
    assert provenance["minimal_chain"]["complete"] is True
    assert readiness == 1.0


def test_datacite_extracted_functions_find_metadata_gaps():
    doi = rop.normalize_datacite_identifier("10.0000/example")
    creators = rop.normalize_datacite_creators([{"name": "Synthetic Author", "orcid": "https://orcid.org/0000"}])
    resource_type = rop.normalize_datacite_resource_type("white paper")
    relations = rop.normalize_datacite_related_identifiers(
        [{"identifier": "10.0000/source", "relation_type": "isVersionOf"}]
    )
    gap = rop.score_datacite_metadata_gap(
        {
            "identifier": doi["identifier"],
            "creators": creators,
            "title": "Synthetic title",
            "publisher": "Synthetic publisher",
            "date": "2026",
            "version": "1",
            "related_identifiers": relations,
        }
    )

    assert doi["identifier_type"] == "DOI"
    assert creators[0]["name"] == "Synthetic Author"
    assert resource_type == "white_paper"
    assert relations[0]["relation_type"] == "isVersionOf"
    assert gap == 0.0


def test_cff_extracted_functions_keep_software_and_science_citation_separate():
    metadata = {
        "title": "Synthetic Synthia package",
        "authors": ["Synthetic Author"],
        "version": "1.0",
        "date": "2026-06-28",
        "identifiers": [{"type": "doi", "value": "10.0000/example"}],
    }
    cff = rop.build_citation_cff_payload(metadata)
    validation = rop.validate_cff_required_fields(cff)
    preferred = rop.build_cff_preferred_citation(metadata, {**metadata, "title": "Synthetic report"})
    references = rop.build_cff_references([{"title": "Source", "url": "https://example.test", "source_id": "source"}])
    readiness = rop.score_cff_citation_readiness(cff)

    assert validation["valid"] is True
    assert preferred["software_citation"]["title"] != preferred["scientific_citation"]["title"]
    assert references[0]["source_id"] == "source"
    assert readiness == 1.0


def test_credit_extracted_functions_preserve_contribution_boundaries():
    contributors = [
        {"name": "Jean-Sebastien Beaulieu", "roles": ["software", "methodology"]},
        {"name": "Prof. Hector Fernando Aguilar", "roles": ["conceptualization", "validation"]},
    ]
    mapped = rop.map_contributor_roles(contributors)
    boundary = rop.build_contribution_boundary(contributors[1])
    load = rop.score_contribution_role_load(contributors)
    summary = rop.render_public_contributor_summary(contributors)

    assert rop.normalize_credit_role("Writing - Review & Editing") == "writing_review_editing"
    assert mapped[0]["roles"] == ["software", "methodology"]
    assert "does not create code authorship" in boundary
    assert load == 0.0
    assert "conceptualization" in summary


def test_academia_upload_extracted_functions_raise_free_platform_risk():
    record = {
        "title": "Synthetic post",
        "abstract": "Summary",
        "co_authors": ["Synthetic Author"],
        "research_interests": ["taxonomy"],
        "file_present": False,
        "post_url": "https://example.test/academia",
        "document_type": "general_post",
    }

    assert rop.classify_academia_upload_record(record) == rop.PlatformType.FREE_ACADEMIC_NETWORK.value
    assert rop.extract_academia_post_metadata(record)["title"] == "Synthetic post"
    assert rop.score_academia_metadata_completeness(record) > 0.5
    assert rop.detect_academia_fileless_or_general_post(record) is True
    assert rop.score_free_platform_risk(record) >= 0.85


def test_academia_rights_extracted_functions_do_not_mark_science_false():
    record = {"url": "https://example.test/source", "version_state": "unknown", "file_present": True}

    assert rop.classify_manuscript_version_state("post-print") == rop.ManuscriptVersionState.POSTPRINT.value
    assert rop.extract_self_archiving_rights_signal(record)["rights_known"] is False
    assert rop.score_rights_uncertainty(record) >= 0.9
    assert rop.separate_accessibility_from_validity(record)["scientifically_validated"] is False
    assert "human review" in rop.build_copyright_review_warning(record)


def test_mit_dspace_extracted_functions_treat_repository_as_provenance_not_peer_review():
    record = {
        "title": "Synthetic item",
        "url": "https://example.test/item",
        "community": "Synthetic community",
        "collection": "Synthetic collection",
        "persistent_url": "https://example.test/handle",
        "institutional_host": True,
        "preservation_signal": True,
        "indexing_signal": True,
        "peer_review_verified": False,
    }
    structure = rop.extract_repository_structure(record)
    boundary = rop.separate_repository_deposit_from_peer_review(record)
    entity = rop.map_repository_to_research_object_entity(record)

    assert rop.classify_institutional_repository_record(record) == rop.PlatformType.INSTITUTIONAL_REPOSITORY.value
    assert structure["community"] == "Synthetic community"
    assert rop.score_repository_preservation_signal(record) == 1.0
    assert boundary["peer_review_verified"] is False
    assert entity["@id"] == "https://example.test/handle"


def test_harvard_dash_extracted_functions_lower_repository_risk():
    dash_record = {
        "persistent_url": "https://example.test/dash",
        "preservation_signal": True,
        "license_note": "Synthetic license",
        "open_download": True,
        "browse_fields": ["author", "title", "date"],
        "google_scholar_indexing": True,
        "catalog_visibility": True,
        "version_state": "preprint",
        "institutional_host": True,
    }
    free_record = {"file_present": False, "document_type": "general_post"}
    signals = rop.extract_dash_discoverability_signals(dash_record)
    comparison = rop.compare_repository_vs_free_platform(dash_record, free_record)

    assert rop.classify_dash_open_access_record(dash_record) == rop.PlatformType.INSTITUTIONAL_REPOSITORY.value
    assert signals["catalog_visibility"] is True
    assert rop.score_dash_persistent_access_signal(dash_record) == 1.0
    assert rop.detect_early_version_priority_signal(dash_record) is True
    assert comparison["repository_lowers_risk"] is True


def test_crossref_extracted_functions_strengthen_registry_status_and_find_mismatch():
    metadata = {
        "doi": "10.0000/example",
        "title": "Registry title",
        "publisher": "Registry publisher",
        "date": "2026",
        "type": "report",
        "author": [{"name": "Registry Author"}],
        "relations": [{"relation_type": "isVersionOf", "identifier": "10.0000/source"}],
        "references": [{"doi": "10.0000/ref"}],
    }
    normalized = rop.normalize_crossref_work_metadata(metadata)
    chain = rop.detect_crossref_relation_chain(metadata)
    mismatch = rop.compare_claim_against_registry_metadata({"title": "Different title"}, metadata)
    status = rop.build_publication_chain_status(
        [
            rop.ResearchSourceEvidence(
                source_id=rop.CROSSREF_SOURCE_ID,
                url="https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
                platform_type=rop.PlatformType.DOI_METADATA_REGISTRY.value,
                title="Crossref",
                claim_type="registry",
                T=0.8,
                I=0.1,
                F=0.0,
                metadata_fields=metadata,
            )
        ]
    )

    assert normalized["doi"] == "10.0000/example"
    assert rop.score_crossref_registry_verification(metadata) == 1.0
    assert chain["chain_present"] is True
    assert mismatch == 1.0
    assert status == rop.ProvenanceStatus.PUBLISHER_OR_REGISTRY_VERIFIED.value


def test_demo_case_is_public_safe_links_all_ten_sources_and_cli_smoke(capsys):
    payload = rop.score_research_object_provenance_case(rop.build_academic_platform_demo_case())
    serialized = json.dumps(payload, ensure_ascii=False).lower()

    assert payload["case_label"] == "Synthetic academic platform provenance case"
    assert set(payload["source_ids"]) == {
        rop.PROV_O_SOURCE_ID,
        rop.RO_CRATE_SOURCE_ID,
        rop.DATACITE_SOURCE_ID,
        rop.CFF_SOURCE_ID,
        rop.CREDIT_SOURCE_ID,
        rop.ACADEMIA_UPLOAD_SOURCE_ID,
        rop.ACADEMIA_COPYRIGHT_SOURCE_ID,
        rop.MIT_DSPACE_SOURCE_ID,
        rop.HARVARD_DASH_SOURCE_ID,
        rop.CROSSREF_SOURCE_ID,
    }
    assert payload["provenance_status"] == rop.ProvenanceStatus.PUBLISHER_OR_REGISTRY_VERIFIED.value
    assert payload["human_review_required"] is True
    assert "no scientific certification" in payload["authority_boundary"]
    forbidden_terms = (
        "raw_" + "private_" + "gmail_" + "body",
        "private_" + "message_" + "id",
        "unpublished " + "manuscript " + "body",
    )
    for term in forbidden_terms:
        assert term not in serialized

    assert main(["research-object-provenance", "demo"]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["human_review_required"] is True

    assert main(["research-object-provenance", "score", "--case", json.dumps({"case_label": "CLI", "evidence_records": []})]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["verification_priority"] == rop.VerificationPriority.CRITICAL_REVIEW.value
