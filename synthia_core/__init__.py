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
    "NeutrosophicSampleSpace",
    "NeutrosophicSetClassifier",
    "NeutrosophicSetMembership",
    "NeutrosophicSetSource",
    "NeutrosophicStatistic",
    "NeutrosophicTruthValue",
    "PlithogenicIProfile",
    "PlithogenicMatrix",
    "SingleValuedNeutrosophicSet",
    "SVNSOperation",
    "SVNSOperator",
    "SymbolicNotation",
    "SystemIndeterminacyChain",
    "TIFNormalizationPolicy",
    "TIF",
    "TIFDependencyProfile",
    "TaxonomicMemorySystem",
]
