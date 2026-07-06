"""Synthia public core package."""

from .lexicon import ILexicon, LexiconBridge, LexiconNode, LexiconSwitchTrace
from .nss import NSSMathRouter, NSSSourceFamily
from .nss_articles import (
    NSSArticleFamilyScore,
    NSSArticleIndex,
    NSSArticleRecord,
    NSSIndexScanResult,
    NSSLexiconDistribution,
    NSSMathIndexScorer,
)
from .independent_neutrosophic_components import IndependentTIFComponentProfile
from .multineutrosophic import MultiNeutrosophicFusion, MultiNeutrosophicSource, MultiTIFAssessment
from .neutrosophic_foundation import (
    NeutrosophicComponent,
    NeutrosophicFoundationSource,
    NeutrosophicProfile,
    NeutrosophicTruthValue,
    TIFNormalizationPolicy,
)
from .neutrosophic_logic import (
    LogicCompatibilityClassifier,
    NeutrosophicLogicProfile,
    NeutrosophicLogicSource,
    NeutrosophicProposition,
)
from .neutrosophic_probability import (
    NeutrosophicEvent,
    NeutrosophicProbability,
    NeutrosophicSampleSpace,
)
from .neutrosophic_random_variables import (
    NeutrosophicRandomVariable,
    NeutrosophicRandomVariableSummary,
    RandomVariableDatum,
)
from .neutrosophic_sets import (
    IFSCompatibilityResult,
    NeutrosophicSetClassifier,
    NeutrosophicSetMembership,
    NeutrosophicSetSource,
    TIFDependencyProfile,
)
from .neutrosophic_statistics import (
    NeutrosophicDatasetProfile,
    NeutrosophicDatum,
    NeutrosophicDistributionProfile,
    NeutrosophicStatistic,
)
from .plithogenic import (
    FractalCarrierProfile,
    IndeterminacyChain,
    MathSource,
    PlithogenicIProfile,
    PlithogenicMatrix,
    SymbolicNotation,
    SystemIndeterminacyChain,
    TIF,
)
from .plithogenic_logic import PlithogenicLogicalProposition, PlithogenicLogicVariable
from .plithogenic_set import PlithogenicAttributeValue, PlithogenicSetProfile
from .algorithm_behavior import (
    AlgorithmBehaviorCase,
    AlgorithmBehaviorReviewer,
    AlgorithmParameterRecord,
    build_algorithmic_bioinformatics_demo_case,
    score_algorithm_behavior_case,
)
from .biology_graph import (
    BiologyGraphEdge,
    BiologyGraphNode,
    BiologyGraphReviewLayer,
    BiologyHyperEdge,
    BiologySuperVertex,
    build_tree_tobacco_demo_graph,
    score_biology_graph_review,
)
from .molecular_evidence import (
    MolecularEvidenceRecord,
    MolecularEvidenceReviewer,
    MolecularReviewCase,
    build_dna_similarity_demo_case,
    score_molecular_review_case,
)
from .neutrino_lexical_gate import (
    DecisionStatus,
    LexPacketNeutrino,
    NeutrinoObservationInput,
    RefusalPacket,
    classify_neutrino_observation,
)
from .phylo_plithogenic import (
    PhyloEvidenceDimension,
    PhyloPlithogenicReviewPacket,
    PhyloPlithogenicReviewer,
    build_tilapia_style_demo_packet,
)
from .risk_triage import (
    RiskCriterion,
    RiskTriageCase,
    RiskTriageReviewer,
    build_food_safety_demo_case,
    score_risk_triage_case,
)
from .research_object_provenance import (
    ResearchObjectProvenanceCase,
    ResearchObjectProvenanceReviewer,
    ResearchSourceEvidence,
    build_academic_platform_demo_case,
    score_research_object_provenance_case,
)
from .scientific_governance import (
    GovernanceEvidenceSource,
    ScientificGovernanceCase,
    ScientificGovernanceReviewer,
    build_synthia_governance_demo_case,
    score_scientific_governance_case,
)
from .novak_anderson_phi_pi import build_novak_anderson_governance_case, score_novak_anderson_governance_case
from .taxonomy_memory import TaxonomicMemorySystem
from .single_valued_neutrosophic import SingleValuedNeutrosophicSet, SVNSOperation, SVNSOperator

HIERARCHY = "I -> I_system^S -> H_lex -> G_lex -> I_lexicon"

__all__ = [
    "HIERARCHY",
    "ILexicon",
    "LexiconBridge",
    "LexiconNode",
    "LexiconSwitchTrace",
    "FractalCarrierProfile",
    "IndeterminacyChain",
    "IndependentTIFComponentProfile",
    "IFSCompatibilityResult",
    "LogicCompatibilityClassifier",
    "MathSource",
    "NSSArticleFamilyScore",
    "NSSArticleIndex",
    "NSSArticleRecord",
    "NSSIndexScanResult",
    "NSSLexiconDistribution",
    "NSSMathRouter",
    "NSSMathIndexScorer",
    "NSSSourceFamily",
    "AlgorithmBehaviorCase",
    "AlgorithmBehaviorReviewer",
    "AlgorithmParameterRecord",
    "BiologyGraphEdge",
    "BiologyGraphNode",
    "BiologyGraphReviewLayer",
    "BiologyHyperEdge",
    "BiologySuperVertex",
    "MolecularEvidenceRecord",
    "MolecularEvidenceReviewer",
    "MolecularReviewCase",
    "MultiNeutrosophicFusion",
    "MultiNeutrosophicSource",
    "MultiTIFAssessment",
    "NeutrosophicComponent",
    "NeutrosophicDatasetProfile",
    "NeutrosophicDatum",
    "NeutrosophicDistributionProfile",
    "NeutrosophicEvent",
    "NeutrosophicFoundationSource",
    "NeutrosophicLogicProfile",
    "NeutrosophicLogicSource",
    "NeutrosophicProbability",
    "NeutrosophicProfile",
    "NeutrosophicProposition",
    "NeutrosophicRandomVariable",
    "NeutrosophicRandomVariableSummary",
    "NeutrosophicSampleSpace",
    "NeutrosophicSetClassifier",
    "NeutrosophicSetMembership",
    "NeutrosophicSetSource",
    "NeutrosophicStatistic",
    "NeutrosophicTruthValue",
    "DecisionStatus",
    "LexPacketNeutrino",
    "NeutrinoObservationInput",
    "RefusalPacket",
    "PlithogenicIProfile",
    "PlithogenicAttributeValue",
    "PhyloEvidenceDimension",
    "PhyloPlithogenicReviewPacket",
    "PhyloPlithogenicReviewer",
    "PlithogenicLogicalProposition",
    "PlithogenicLogicVariable",
    "PlithogenicMatrix",
    "PlithogenicSetProfile",
    "RandomVariableDatum",
    "RiskCriterion",
    "RiskTriageCase",
    "RiskTriageReviewer",
    "ResearchObjectProvenanceCase",
    "ResearchObjectProvenanceReviewer",
    "ResearchSourceEvidence",
    "GovernanceEvidenceSource",
    "ScientificGovernanceCase",
    "ScientificGovernanceReviewer",
    "SingleValuedNeutrosophicSet",
    "SVNSOperation",
    "SVNSOperator",
    "SymbolicNotation",
    "SystemIndeterminacyChain",
    "TIFNormalizationPolicy",
    "TIF",
    "TIFDependencyProfile",
    "TaxonomicMemorySystem",
    "build_algorithmic_bioinformatics_demo_case",
    "build_academic_platform_demo_case",
    "build_food_safety_demo_case",
    "build_dna_similarity_demo_case",
    "classify_neutrino_observation",
    "build_novak_anderson_governance_case",
    "build_synthia_governance_demo_case",
    "build_tilapia_style_demo_packet",
    "build_tree_tobacco_demo_graph",
    "score_biology_graph_review",
    "score_algorithm_behavior_case",
    "score_molecular_review_case",
    "score_research_object_provenance_case",
    "score_risk_triage_case",
    "score_novak_anderson_governance_case",
    "score_scientific_governance_case",
]
