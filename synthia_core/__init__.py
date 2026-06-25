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
from .neutrosophic_sets import (
    IFSCompatibilityResult,
    NeutrosophicSetClassifier,
    NeutrosophicSetMembership,
    NeutrosophicSetSource,
    TIFDependencyProfile,
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
    "NeutrosophicFoundationSource",
    "NeutrosophicProfile",
    "NeutrosophicSetClassifier",
    "NeutrosophicSetMembership",
    "NeutrosophicSetSource",
    "NeutrosophicTruthValue",
    "PlithogenicIProfile",
    "PlithogenicMatrix",
    "SymbolicNotation",
    "SystemIndeterminacyChain",
    "TIFNormalizationPolicy",
    "TIF",
    "TIFDependencyProfile",
    "TaxonomicMemorySystem",
]
