"""Domain classification surface — pure rules, no persistence (ADR-008 Wave 4).

Implementation remains in ``app.classification.*`` (Session-free). Import from
here in application/ingestion so the dependency points at the domain facade.
"""

from app.classification.language_rules import extract_language_requirements
from app.classification.rules import ClassificationResult, classify_job
from app.classification.taxonomy import TAXONOMY, build_alias_index

__all__ = [
    "ClassificationResult",
    "TAXONOMY",
    "build_alias_index",
    "classify_job",
    "extract_language_requirements",
]
