"""
DSPy modules for systematic prompt optimization.
"""

from .cover_letter import (
    CoverLetterSignature,
    CoverLetterGenerator, 
    CoverLetterOptimizer,
    cover_letter_quality_metric,
    get_cover_letter_optimizer
)

__all__ = [
    "CoverLetterSignature",
    "CoverLetterGenerator",
    "CoverLetterOptimizer", 
    "cover_letter_quality_metric",
    "get_cover_letter_optimizer"
]