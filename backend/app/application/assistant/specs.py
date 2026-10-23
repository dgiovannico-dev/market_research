"""Pydantic contracts for MCP-proposed dashboards and reports."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

WidgetType = Literal["chart", "table", "kpi", "quality"]
ViewMode = Literal["guided", "trends_only"]
ReportSectionKind = Literal["summary", "rates", "skills", "sources", "gaps", "custom"]
NarrativePolicy = Literal["observed_only"]


class DashboardFilters(BaseModel):
    technologies: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    source_keys: list[str] = Field(default_factory=list)
    contract_types: list[str] = Field(default_factory=list)


class DashboardWidget(BaseModel):
    id: str
    type: WidgetType
    metric_key: str
    params: dict[str, Any] = Field(default_factory=dict)


class SpecGrounding(BaseModel):
    sample_size: int | None = None
    queries_used: list[str] = Field(default_factory=list)
    endpoints_used: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class DashboardSpec(BaseModel):
    title: str
    period_days: int = Field(default=90, ge=1, le=3660)
    view_mode: ViewMode = "guided"
    filters: DashboardFilters = Field(default_factory=DashboardFilters)
    widgets: list[DashboardWidget] = Field(default_factory=list)
    disclaimer_mode: ViewMode | None = None
    grounding: SpecGrounding = Field(default_factory=SpecGrounding)

    @model_validator(mode="after")
    def inherit_disclaimer_mode(self) -> DashboardSpec:
        if self.disclaimer_mode is None:
            self.disclaimer_mode = self.view_mode
        return self


class ReportSection(BaseModel):
    kind: ReportSectionKind
    title: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class ReportSpec(BaseModel):
    title: str
    period_days: int = Field(default=90, ge=1, le=3660)
    sections: list[ReportSection] = Field(default_factory=list)
    include_profile_gaps: bool = False
    grounding: SpecGrounding = Field(default_factory=SpecGrounding)
    narrative_policy: NarrativePolicy = "observed_only"

    @field_validator("narrative_policy")
    @classmethod
    def only_observed(cls, v: str) -> str:
        if v != "observed_only":
            raise ValueError("narrative_policy must be observed_only")
        return v


class IntentHints(BaseModel):
    """Structured hints the LLM (or a naive parser) passes to proposers."""

    title: str | None = None
    period_days: int = 90
    view_mode: ViewMode = "guided"
    technologies: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    source_keys: list[str] = Field(default_factory=list)
    contract_types: list[str] = Field(default_factory=list)
    include_rates: bool = True
    include_trends: bool = True
    include_quality: bool = False
    include_profile_gaps: bool = False
    user_prompt: str | None = None
