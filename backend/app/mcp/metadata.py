"""Schema introspection from SQLAlchemy mapped metadata."""

from __future__ import annotations

from typing import Any

# Ensure all models are registered on Base.metadata
import app.storage.models  # noqa: F401
from app.storage.db import Base


def get_db_metadata() -> dict[str, Any]:
    tables_out: list[dict[str, Any]] = []
    for table in Base.metadata.sorted_tables:
        columns = [
            {
                "name": col.name,
                "type": str(col.type),
                "nullable": bool(col.nullable),
                "primary_key": bool(col.primary_key),
            }
            for col in table.columns
        ]
        fks = [
            {
                "constrained_columns": [fk.parent.name] if fk.parent is not None else [],
                "referred_table": fk.column.table.name if fk.column is not None else None,
                "referred_columns": [fk.column.name] if fk.column is not None else [],
            }
            for fk in table.foreign_keys
        ]
        tables_out.append(
            {
                "name": table.name,
                "columns": columns,
                "foreign_keys": fks,
            }
        )
    return {
        "dialect": "postgresql",
        "table_count": len(tables_out),
        "tables": tables_out,
        "source": "sqlalchemy_metadata",
    }
