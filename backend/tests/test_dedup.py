from app.ingestion.service import find_duplicate
from app.normalization.hashing import content_hash
from app.normalization.url import canonicalize_url


def test_url_and_hash_helpers_for_dedup():
    a = canonicalize_url("https://jobs.example/a?utm_campaign=1")
    b = canonicalize_url("https://jobs.example/a")
    assert a == b
    assert content_hash("Same body") == content_hash("same   body")
