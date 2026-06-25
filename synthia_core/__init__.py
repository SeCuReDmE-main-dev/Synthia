"""Synthia public core package."""

from .lexicon import ILexicon, LexiconBridge, LexiconNode, LexiconSwitchTrace
from .plithogenic import TIF, PlithogenicMatrix
from .taxonomy_memory import TaxonomicMemorySystem

HIERARCHY = "I -> I_system^S -> D_f -> dF -> i_fractal"

__all__ = [
    "HIERARCHY",
    "ILexicon",
    "LexiconBridge",
    "LexiconNode",
    "LexiconSwitchTrace",
    "PlithogenicMatrix",
    "TIF",
    "TaxonomicMemorySystem",
]
