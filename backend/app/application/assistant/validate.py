"""Validate DashboardSpec / ReportSpec against semantic catalog and policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import get_args

from app.application.assistant.semantics import metric_keys
from app.application.assistant.specs import DashboardSpec, ReportSpec, WidgetType

_WIDGET_TYPES: set[str] = set(get_args(WidgetType))


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"ok": self.ok, "errors": self.errors, "warnings": self.warnings}


def validate_spec(spec: DashboardSpec | ReportSpec | dict) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    keys = metric_keys()

    if isinstance(spec, dict):
        if "widgets" in spec or spec.get("view_mode"):
            try:
                spec = DashboardSpec.model_validate(spec)
            except Exception as exc:  # noqa: BLE001
                return ValidationResult(ok=False, errors=[f"invalid DashboardSpec: {exc}"])
        else:
            try:
                spec = ReportSpec.model_validate(spec)
            except Exception as exc:  # noqa: BLE001
                return ValidationResult(ok=False, errors=[f"invalid ReportSpec: {exc}"])

    if isinstance(spec, DashboardSpec):
        if not spec.widgets:
            warnings.append("dashboard has no widgets")
        for w in spec.widgets:
            if w.type not in _WIDGET_TYPES:
                errors.append(f"unknown widget.type: {w.type}")
            if w.metric_key not in keys:
                errors.append(f"unknown metric_key: {w.metric_key}")
        if spec.view_mode == "trends_only" and any(
            w.metric_key == "data_quality" for w in spec.widgets
        ):
            warnings.append("data_quality widget unusual in trends_only mode")
    elif isinstance(spec, ReportSpec):
        if spec.narrative_policy != "observed_only":
            errors.append("narrative_policy must be observed_only")
        if not spec.sections:
            warnings.append("report has no sections")
        for sec in spec.sections:
            if sec.kind == "rates":
                warnings.append(
                    "rates section must use non-NULL observed rates only; never invent medians"
                )
    else:
        errors.append("unsupported spec type")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings)
