"""Synthia public core package."""

from .lexicon import ILexicon, LexiconBridge, LexiconNode, LexiconSwitchTrace
from .nss import NSSMathRouter, NSSSourceFamily
from .plithogenic import (
    FractalCarrierProfile,
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
    "MathSource",
    "NSSMathRouter",
    "NSSSourceFamily",
    "PlithogenicIProfile",
    "PlithogenicMatrix",
    "SymbolicNotation",
    "SystemIndeterminacyChain",
    "TIF",
    "TaxonomicMemorySystem",
]
