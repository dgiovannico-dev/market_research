import enum


class EvidenceKind(str, enum.Enum):
    observed = "observed"
    extracted = "extracted"
    inferred = "inferred"
    derived = "derived"
    estimated = "estimated"
    manually_verified = "manually_verified"


class JobStatus(str, enum.Enum):
    active_verified = "active_verified"
    active_unverified = "active_unverified"
    stale = "stale"
    closed = "closed"
    removed_from_source = "removed_from_source"
    unknown = "unknown"


class ContractType(str, enum.Enum):
    freelance = "freelance"
    b2b = "b2b"
    contractor = "contractor"
    employment = "employment"
    temporary = "temporary"
    unknown = "unknown"


class RemoteType(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"
    unknown = "unknown"


class SkillImportance(str, enum.Enum):
    required = "required"
    preferred = "preferred"
    mentioned = "mentioned"


class RateUnit(str, enum.Enum):
    hour = "hour"
    day = "day"
    month = "month"
    year = "year"
    project = "project"
    unknown = "unknown"


class RateType(str, enum.Enum):
    advertised = "advertised"
    estimated = "estimated"
    manually_reported = "manually_reported"


class CollectionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    partial = "partial"


class ConnectorStatus(str, enum.Enum):
    enabled = "enabled"
    disabled = "disabled"
    unsupported = "unsupported"
    requires_credentials = "requires_credentials"
    manual_import = "manual_import"
    error = "error"


class ResidenceAccess(str, enum.Enum):
    explicitly_allowed = "explicitly_allowed"
    explicitly_restricted = "explicitly_restricted"
    unclear = "unclear"
    not_applicable = "not_applicable"
