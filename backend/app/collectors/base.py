from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class RawJob:
    source_job_id: str
    url: str
    title: str
    company: str | None = None
    description: str | None = None
    location: str | None = None
    published_at: datetime | None = None
    salary_text: str | None = None
    tags: list[str] = field(default_factory=list)
    job_type: str | None = None
    remote_hint: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollectorResult:
    records: list[RawJob]
    pages_scanned: int = 1
    errors: list[str] = field(default_factory=list)


class BaseCollector(ABC):
    name: str
    source_key: str

    @abstractmethod
    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        raise NotImplementedError
