"""Build a downloadable PDF preview for assistant ReportSpec proposals."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Literal, Optional

from fpdf import FPDF
from sqlalchemy.orm import Session

from app.application.assistant.dashboard_narrative import narrate_dashboard
from app.application.assistant.materialize import materialize_report
from app.application.assistant.propose import propose_report
from app.reports.weekly import format_pct

Locale = Literal["en", "it"]


def _font_paths() -> tuple[Path, Path]:
    """Resolve DejaVu for Unicode (IT accents). Prefer system package, then vendored."""
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu"),
        Path(__file__).resolve().parents[2] / "assets" / "fonts",
    ]
    for font_dir in candidates:
        regular = font_dir / "DejaVuSans.ttf"
        bold = font_dir / "DejaVuSans-Bold.ttf"
        if regular.is_file():
            return regular, bold if bold.is_file() else regular
    raise RuntimeError(
        "DejaVuSans.ttf not found (install fonts-dejavu-core or vendor under app/assets/fonts)"
    )


class _ReportDoc(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        regular, bold = _font_paths()
        self.add_font("DejaVu", "", str(regular))
        self.add_font("DejaVu", "B", str(bold))
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(18, 18, 18)

    def footer(self) -> None:  # noqa: N802 — fpdf hook
        self.set_y(-12)
        self.set_x(self.l_margin)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(self.epw, 8, f"{self.page_no()}", align="C")


def _write(pdf: _ReportDoc, text: str, *, size: int = 10, bold: bool = False) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.set_text_color(20 if bold else 30, 20 if bold else 30, 20 if bold else 30)
    clean = (text or "").replace("\r", "").strip() or "—"
    line_h = max(4.5, size * 0.5)
    pdf.multi_cell(pdf.epw, line_h, clean)
    pdf.ln(1.5)


def _heading(pdf: _ReportDoc, text: str, *, size: int = 14) -> None:
    _write(pdf, text, size=size, bold=True)


def _body(pdf: _ReportDoc, text: str, *, size: int = 10) -> None:
    _write(pdf, text, size=size, bold=False)


def _bullet(pdf: _ReportDoc, text: str) -> None:
    _write(pdf, f"- {text}", size=10, bold=False)


def render_report_pdf(
    *,
    title: str,
    period_days: int,
    narrative: str,
    narrative_source: str,
    sections: list[dict[str, Any]],
    counts: dict[str, Any],
    rising: list[dict[str, Any]],
    cooling: list[dict[str, Any]],
    disclaimer: str | None,
    locale: Locale,
    prompt: str,
) -> bytes:
    pdf = _ReportDoc()
    pdf.add_page()

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    brand = "Freelance Market Intelligence"
    _heading(pdf, brand, size=11)
    _heading(pdf, title or "Observed market report", size=16)
    meta_it = f"Finestra {period_days}g · generato {generated} · narrativa: {narrative_source}"
    meta_en = f"{period_days}d window · generated {generated} · narrative: {narrative_source}"
    _body(pdf, meta_it if locale == "it" else meta_en, size=9)

    if prompt.strip():
        _heading(pdf, "Richiesta" if locale == "it" else "Request", size=12)
        _body(pdf, prompt.strip()[:800], size=9)

    _heading(pdf, "In linguaggio semplice" if locale == "it" else "In plain language", size=12)
    _body(pdf, (narrative or "").strip() or ("—"), size=10)

    jobs_n = counts.get("unique_jobs_in_period")
    rates_n = counts.get("jobs_with_rate_in_period")
    sources_n = counts.get("sources_enabled")
    _heading(pdf, "Evidenza osservata" if locale == "it" else "Observed evidence", size=12)
    if locale == "it":
        _bullet(pdf, f"Annunci unici nel periodo: {jobs_n}")
        _bullet(pdf, f"Con tariffa dichiarata: {rates_n}")
        _bullet(pdf, f"Sorgenti abilitate: {sources_n}")
    else:
        _bullet(pdf, f"Unique jobs in period: {jobs_n}")
        _bullet(pdf, f"Jobs with declared rate: {rates_n}")
        _bullet(pdf, f"Enabled sources: {sources_n}")

    if sections:
        _heading(pdf, "Sezioni report" if locale == "it" else "Report sections", size=12)
        for sec in sections:
            label = sec.get("title") or sec.get("kind") or "section"
            note = ""
            if sec.get("insufficient_data"):
                note = " — dati insufficienti" if locale == "it" else " — insufficient data"
            extra = sec.get("note")
            line = f"{label}{note}"
            if isinstance(sec.get("data"), dict) and sec["data"]:
                bits = ", ".join(f"{k}={v}" for k, v in list(sec["data"].items())[:4])
                line = f"{line}: {bits}"
            _bullet(pdf, line)
            if extra:
                _body(pdf, str(extra), size=8)

    if rising or cooling:
        _heading(
            pdf,
            "Tecnologie (crescita / calo)" if locale == "it" else "Technologies (rising / cooling)",
            size=12,
        )
        for row in rising[:8]:
            _bullet(
                pdf,
                f"↑ {row.get('technology')}: {format_pct(row.get('growth_pct'), locale=locale)} "
                f"(n={row.get('sample_size')})",
            )
        for row in cooling[:8]:
            _bullet(
                pdf,
                f"↓ {row.get('technology')}: {format_pct(row.get('growth_pct'), locale=locale)} "
                f"(n={row.get('sample_size')})",
            )

    _heading(pdf, "Limiti" if locale == "it" else "Limits", size=12)
    default_disc = (
        "Queste cifre descrivono solo gli annunci osservati in FMI, non la dimensione totale del mercato."
        if locale == "it"
        else "These figures describe observed FMI ads only, not total market size."
    )
    _body(pdf, (disclaimer or "").strip() or default_disc, size=9)

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


async def build_report_pdf(
    db: Session,
    *,
    prompt: str,
    locale: Locale = "en",
    country_code: Optional[str] = None,
) -> dict[str, Any]:
    """Propose + materialize + narrate, then render PDF bytes."""
    text = (prompt or "").strip()
    if not text:
        raise ValueError("prompt is required")

    spec = propose_report(text)
    materialized = materialize_report(db, spec)
    if not materialized.get("ok"):
        raise ValueError(
            "; ".join(materialized.get("errors") or ["report materialization failed"])
        )

    narr = await narrate_dashboard(
        db,
        period_days=int(spec.period_days),
        user_prompt=text,
        locale=locale,
        country_code=country_code,
    )
    evidence = narr.get("evidence") or {}
    pdf_bytes = render_report_pdf(
        title=spec.title,
        period_days=int(spec.period_days),
        narrative=str(narr.get("narrative") or materialized.get("narrative") or ""),
        narrative_source=str(narr.get("source") or "deterministic"),
        sections=list(materialized.get("sections") or []),
        counts=dict(materialized.get("counts") or {}),
        rising=list(evidence.get("rising") or []),
        cooling=list(evidence.get("cooling") or []),
        disclaimer=evidence.get("disclaimer"),
        locale=locale,
        prompt=text,
    )
    filename = f"fmi-report-{spec.period_days}d.pdf"
    return {
        "pdf_bytes": pdf_bytes,
        "filename": filename,
        "spec": spec.model_dump(),
        "materialized": materialized,
        "narrative_source": narr.get("source"),
        "meta": {"locale": locale},
    }
