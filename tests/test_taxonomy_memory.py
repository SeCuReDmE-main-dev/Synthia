from synthia_core.taxonomy_memory import (
    AIAssistanceDisclosure,
    AIAssistanceDisclosureTracker,
    CitationTraceAuditor,
    IndeterminacyLocator,
    IntegralConservationLinker,
    MemoryRepairClassifier,
    MultilingualTaxonomyBridge,
    PriorityVsMemoryBoundary,
    TaxonomicMemorySystem,
    TaxonomicReviewPacketBuilder,
)


def test_aburria_anchor_preserves_formal_authority_and_redescription_trace():
    system = TaxonomicMemorySystem()
    record = system.build_aburria_anchor()
    packet = TaxonomicReviewPacketBuilder().build(record)

    assert packet["formal_name"] == "Aburria aburri"
    assert record.formal_authority == "Lesson, 1828"
    assert record.redescriptions[0].critical_redescription == "Aguilar H. F. & R. F. Aguilar 2012"
    assert packet["human_review_required"] is True


def test_memory_repair_classifier_and_boundary():
    trace = TaxonomicMemorySystem().build_aburria_anchor().redescriptions[0]
    annotation = PriorityVsMemoryBoundary().annotate(trace)

    assert "morphology" in trace.repair_types
    assert "nesting" in trace.repair_types
    assert annotation["formal_authority_preserved"] == "Lesson, 1828"
    assert annotation["can_transfer_formal_authorship"] is False


def test_indeterminacy_locator_keeps_sources_specific():
    located = IndeterminacyLocator().locate("The diagnosis is incomplete and the subspecies boundary is contested.")

    assert "incomplete_diagnosis" in located["sources"]
    assert "species_subspecies_boundary" in located["sources"]
    assert located["tif"]["hierarchy"] == "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"


def test_citation_trace_auditor_flags_missing_context():
    record = TaxonomicMemorySystem().build_aburria_anchor()
    audit = CitationTraceAuditor().audit("Aburria aburri is discussed here.", [record])

    assert audit["missing_author_date"] is True
    assert audit["hidden_redescriptions"] == ["Aburria aburri"]
    assert audit["human_review_required"] is True


def test_white_paper_support_helpers():
    trace = TaxonomicMemorySystem().build_aburria_anchor().redescriptions[0]
    link = IntegralConservationLinker().link(trace)
    bridge = MultilingualTaxonomyBridge().bridge("taxonomic memory repair")
    tracker = AIAssistanceDisclosureTracker()

    tracker.record(AIAssistanceDisclosure("OpenAI Codex", "Codex native", "2026-06-25", "source organization"))

    assert "conservation report" in link["actions"]
    assert bridge["translations"]["es"] == "reparacion de memoria taxonomica"
    assert tracker.as_list()[0]["human_verified"] is False
