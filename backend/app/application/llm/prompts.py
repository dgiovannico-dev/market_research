"""Prompt registry CRUD + resolve active version."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.llm.defaults import SEED_PROMPTS, render_template
from app.storage.models_llm import LlmAdminAudit, LlmPromptTemplate, LlmPromptVersion


def ensure_seed_prompts(db: Session) -> dict[str, Any]:
    created = 0
    for seed in SEED_PROMPTS:
        existing = db.scalar(
            select(LlmPromptTemplate).where(LlmPromptTemplate.slug == seed["slug"])
        )
        if existing:
            continue
        tmpl = LlmPromptTemplate(
            slug=seed["slug"],
            purpose=seed["purpose"],
            description=seed.get("description"),
        )
        db.add(tmpl)
        db.flush()
        ver = LlmPromptVersion(
            template_id=tmpl.id,
            version=1,
            system_text=seed["system_text"],
            user_text=seed["user_text"],
            status="active",
            notes="seed v1",
            created_by="system",
        )
        db.add(ver)
        db.flush()
        tmpl.active_version_id = ver.id
        created += 1
    if created:
        db.commit()
    return {"seeded": created}


def list_templates(db: Session) -> list[dict[str, Any]]:
    ensure_seed_prompts(db)
    rows = db.scalars(select(LlmPromptTemplate).order_by(LlmPromptTemplate.slug)).all()
    out = []
    for t in rows:
        versions = db.scalars(
            select(LlmPromptVersion)
            .where(LlmPromptVersion.template_id == t.id)
            .order_by(LlmPromptVersion.version.desc())
        ).all()
        out.append(
            {
                "id": t.id,
                "slug": t.slug,
                "purpose": t.purpose,
                "description": t.description,
                "active_version_id": t.active_version_id,
                "versions": [_version_public(v) for v in versions],
            }
        )
    return out


def _version_public(v: LlmPromptVersion) -> dict[str, Any]:
    return {
        "id": v.id,
        "template_id": v.template_id,
        "version": v.version,
        "system_text": v.system_text,
        "user_text": v.user_text,
        "status": v.status,
        "notes": v.notes,
        "created_by": v.created_by,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def create_version(
    db: Session,
    *,
    slug: str,
    system_text: str,
    user_text: str,
    notes: Optional[str] = None,
    actor: Optional[str] = None,
    activate: bool = False,
) -> dict[str, Any]:
    ensure_seed_prompts(db)
    tmpl = db.scalar(select(LlmPromptTemplate).where(LlmPromptTemplate.slug == slug))
    if not tmpl:
        raise ValueError(f"unknown prompt slug: {slug}")
    latest = db.scalar(
        select(LlmPromptVersion)
        .where(LlmPromptVersion.template_id == tmpl.id)
        .order_by(LlmPromptVersion.version.desc())
        .limit(1)
    )
    next_v = (latest.version + 1) if latest else 1
    ver = LlmPromptVersion(
        template_id=tmpl.id,
        version=next_v,
        system_text=system_text,
        user_text=user_text,
        status="draft",
        notes=notes,
        created_by=actor,
    )
    db.add(ver)
    db.flush()
    if activate:
        _activate(db, tmpl, ver, actor=actor)
    else:
        db.commit()
    db.refresh(ver)
    return _version_public(ver)


def activate_version(
    db: Session,
    *,
    version_id: int,
    actor: Optional[str] = None,
) -> dict[str, Any]:
    ver = db.get(LlmPromptVersion, version_id)
    if not ver:
        raise ValueError("version not found")
    tmpl = db.get(LlmPromptTemplate, ver.template_id)
    if not tmpl:
        raise ValueError("template not found")
    _activate(db, tmpl, ver, actor=actor)
    return _version_public(ver)


def _activate(
    db: Session,
    tmpl: LlmPromptTemplate,
    ver: LlmPromptVersion,
    *,
    actor: Optional[str],
) -> None:
    for other in db.scalars(
        select(LlmPromptVersion).where(
            LlmPromptVersion.template_id == tmpl.id,
            LlmPromptVersion.status == "active",
        )
    ).all():
        other.status = "archived"
    ver.status = "active"
    tmpl.active_version_id = ver.id
    db.add(
        LlmAdminAudit(
            action="prompt_activate",
            actor=actor,
            details={"slug": tmpl.slug, "version": ver.version, "version_id": ver.id},
        )
    )
    db.commit()


def archive_version(
    db: Session,
    *,
    version_id: int,
    actor: Optional[str] = None,
) -> dict[str, Any]:
    ver = db.get(LlmPromptVersion, version_id)
    if not ver:
        raise ValueError("version not found")
    tmpl = db.get(LlmPromptTemplate, ver.template_id)
    if tmpl and tmpl.active_version_id == ver.id:
        raise ValueError("cannot archive the active version; activate another first")
    ver.status = "archived"
    db.add(
        LlmAdminAudit(
            action="prompt_archive",
            actor=actor,
            details={"version_id": version_id},
        )
    )
    db.commit()
    return _version_public(ver)


def delete_version(
    db: Session,
    *,
    version_id: int,
    actor: Optional[str] = None,
) -> dict[str, Any]:
    ver = db.get(LlmPromptVersion, version_id)
    if not ver:
        raise ValueError("version not found")
    if ver.status == "active":
        raise ValueError("cannot delete active version")
    db.delete(ver)
    db.add(
        LlmAdminAudit(
            action="prompt_delete",
            actor=actor,
            details={"version_id": version_id},
        )
    )
    db.commit()
    return {"status": "deleted", "version_id": version_id}


def resolve_prompt(
    db: Session,
    *,
    slug: str,
    variables: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    ensure_seed_prompts(db)
    tmpl = db.scalar(select(LlmPromptTemplate).where(LlmPromptTemplate.slug == slug))
    if not tmpl or not tmpl.active_version_id:
        raise ValueError(f"no active prompt for slug={slug}")
    ver = db.get(LlmPromptVersion, tmpl.active_version_id)
    if not ver:
        raise ValueError(f"active prompt missing for slug={slug}")
    vars_ = variables or {}
    return {
        "slug": slug,
        "version": ver.version,
        "version_id": ver.id,
        "system": render_template(ver.system_text, vars_),
        "user": render_template(ver.user_text, vars_),
    }
