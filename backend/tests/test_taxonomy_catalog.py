"""Taxonomy catalog integrity + expanded domain coverage."""

from __future__ import annotations

from app.classification.rules import classify_job
from app.classification.taxonomy import TAXONOMY, build_alias_index


def test_taxonomy_canonical_names_unique():
    names = [t["canonical_name"] for t in TAXONOMY]
    assert len(names) == len(set(names))


def test_taxonomy_covers_software_cyber_ai_categories():
    cats = {t["category"] for t in TAXONOMY}
    assert "programming_languages" in cats
    assert "security" in cats
    assert "ai" in cats or "llm_frameworks" in cats
    assert "ml_frameworks" in cats or "mlops" in cats


def test_alias_index_maps_expanded_domains():
    index = build_alias_index()
    assert index["pytorch"] == "PyTorch"
    assert index["pentest"] == "Penetration Testing"
    assert index["devsecops"] == "DevSecOps"
    assert index["genai"] == "Generative AI"
    assert index["nestjs"] == "NestJS"
    assert index["siem"] == "SIEM"


def test_classify_detects_cyber_and_ai_aliases():
    result = classify_job(
        title="AppSec / DevSecOps Engineer",
        description=(
            "OWASP Top 10, SIEM/SOAR, Snyk and Trivy in the pipeline. "
            "Also RAG with LangChain, Pinecone, and PyTorch fine-tuning."
        ),
        location="Remote EU",
    )
    names = {t["canonical_name"] for t in result.technologies}
    assert "AppSec" in names or "DevSecOps" in names or "OWASP" in names
    assert "SIEM" in names or "SOAR" in names
    assert "LangChain" in names or "RAG" in names or "PyTorch" in names
