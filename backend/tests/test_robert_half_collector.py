"""Unit tests for Robert Half XML parsing (no live network)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from app.collectors.robert_half import _parse_posting

_SAMPLE = """<?xml version="1.0"?>
<SEP>
  <JobPositionPosting>
    <JobPositionPostingId>06680-0013516804</JobPositionPostingId>
    <JobPositionPostDate>06/10/2026</JobPositionPostDate>
    <HiringOrg>
      <HiringOrgName>Kaufmännischer Bereich</HiringOrgName>
      <WebSite>https://www.roberthalf.ch/</WebSite>
    </HiringOrg>
    <JobPositionInformation>
      <JobPositionTitle>Technischer Verkaufsberater (w/m/d)</JobPositionTitle>
      <JobPositionDescription>
        <JobPositionLocation>
          <Location>Zürich</Location>
          <Region>Zürich</Region>
          <CountryCode>CH</CountryCode>
        </JobPositionLocation>
        <CompensationDescription>
          <SalaryMinimum>CHF0</SalaryMinimum>
          <SalaryMaximum>CHF0</SalaryMaximum>
          <SalaryPeriod>Yearly</SalaryPeriod>
          <SalaryCurrency>CHF</SalaryCurrency>
        </CompensationDescription>
        <FullDescription><p>Hello</p></FullDescription>
      </JobPositionDescription>
    </JobPositionInformation>
    <HowToApply>
      <ApplicationMethods>
        <ByWeb>
          <URL>https://www.roberthalf.com/ch/de/job/example</URL>
        </ByWeb>
      </ApplicationMethods>
    </HowToApply>
  </JobPositionPosting>
</SEP>
"""


def test_parse_posting_extracts_core_fields():
    root = ET.fromstring(_SAMPLE)
    posting = root.find("JobPositionPosting")
    assert posting is not None
    job = _parse_posting(posting, "ch")
    assert job is not None
    assert job.source_job_id == "rh-ch-06680-0013516804"
    assert job.title.startswith("Technischer")
    assert job.url.startswith("https://www.roberthalf.com/")
    assert "Zürich" in (job.location or "")
    assert job.company == "Kaufmännischer Bereich"
    assert job.description == "Hello"
