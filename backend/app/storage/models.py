"""Aggregate model imports for Alembic and application use."""

from app.storage.models_core import (
    CollectionRun,
    CrawlerTick,
    Job,
    JobIntentMatch,
    SearchQuery,
    Source,
    SourceCredential,
    SourceVerification,
)
from app.storage.models_skills import (
    DuplicateGroup,
    JobRate,
    JobSkill,
    JobSnapshot,
    MarketMetricDaily,
    Technology,
)
from app.storage.models_user import (
    AlertRule,
    ApplicationOutcome,
    AuditLog,
    LlmModel,
    SavedFilter,
    UserProfile,
    UserSkill,
)

__all__ = [
    "Source",
    "SourceCredential",
    "SourceVerification",
    "SearchQuery",
    "JobIntentMatch",
    "CollectionRun",
    "CrawlerTick",
    "Job",
    "Technology",
    "JobSkill",
    "JobRate",
    "JobSnapshot",
    "MarketMetricDaily",
    "DuplicateGroup",
    "UserProfile",
    "UserSkill",
    "ApplicationOutcome",
    "SavedFilter",
    "AlertRule",
    "LlmModel",
    "AuditLog",
]
