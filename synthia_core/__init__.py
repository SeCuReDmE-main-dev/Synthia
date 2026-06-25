"""Synthia public core package."""

from .lexicon import ILexicon, LexiconBridge, LexiconNode, LexiconSwitchTrace
from .plithogenic import IndeterminacyChain, MathSource, PlithogenicIProfile, PlithogenicMatrix, SymbolicNotation, TIF
from .taxonomy_memory import TaxonomicMemorySystem

HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"

__all__ = [
    "HIERARCHY",
    "ILexicon",
    "LexiconBridge",
    "LexiconNode",
    "LexiconSwitchTrace",
    "IndeterminacyChain",
    "MathSource",
    "PlithogenicIProfile",
    "PlithogenicMatrix",
    "SymbolicNotation",
    "TIF",
    "TaxonomicMemorySystem",
]
