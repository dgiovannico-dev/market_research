from app.mcp.metadata import get_db_metadata


def test_metadata_includes_core_tables():
    meta = get_db_metadata()
    names = {t["name"] for t in meta["tables"]}
    assert "jobs" in names
    assert "sources" in names
    assert "job_rates" in names
    assert "job_skills" in names
    jobs = next(t for t in meta["tables"] if t["name"] == "jobs")
    col_names = {c["name"] for c in jobs["columns"]}
    assert "title_original" in col_names
    assert "published_at" in col_names
