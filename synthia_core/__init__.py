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
    "NeutrosophicTruthValue",
    "PlithogenicIProfile",
    "PlithogenicMatrix",
    "SymbolicNotation",
    "SystemIndeterminacyChain",
    "TIFNormalizationPolicy",
    "TIF",
    "TaxonomicMemorySystem",
]
