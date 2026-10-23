"""Pure unit tests for geo country DSS smoke helpers."""

from __future__ import annotations

from app.ops.geo_country_smoke import (
    aggregate_known_by_connector,
    evaluate_geo_country,
    exit_code_for_verdicts,
)


def test_aggregate_known_by_connector_weights_pct():
    rows = [
        {"connector_type": "okemprego", "n": 50, "pct_known_country": 100.0},
        {"connector_type": "okemprego", "n": 50, "pct_known_country": 80.0},
        {"connector_type": "other", "n": 10, "pct_known_country": 0.0},
    ]
    agg = aggregate_known_by_connector(rows)
    assert agg["okemprego"] == (100, 90.0)
    assert agg["other"] == (10, 0.0)


def test_evaluate_skip_when_zero_jobs():
    verdicts = evaluate_geo_country([])
    assert all(v.status == "SKIP" for v in verdicts)
    assert exit_code_for_verdicts(verdicts) == 0


def test_evaluate_pass_at_threshold():
    rows = [
        {"connector_type": "jobbank_ca", "n": 20, "pct_known_country": 95.0},
        {"connector_type": "viewjobs", "n": 10, "pct_known_country": 100.0},
    ]
    verdicts = evaluate_geo_country(
        rows, connectors=("jobbank_ca", "viewjobs", "okemprego")
    )
    by = {v.connector_type: v for v in verdicts}
    assert by["jobbank_ca"].status == "PASS"
    assert by["viewjobs"].status == "PASS"
    assert by["okemprego"].status == "SKIP"
    assert exit_code_for_verdicts(verdicts) == 0


def test_evaluate_fail_below_threshold():
    rows = [{"connector_type": "devglobaljobs", "n": 15, "pct_known_country": 80.0}]
    verdicts = evaluate_geo_country(rows, connectors=("devglobaljobs",))
    assert verdicts[0].status == "FAIL"
    assert exit_code_for_verdicts(verdicts) == 1
