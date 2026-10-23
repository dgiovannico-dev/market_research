"""Home-market ISO2 for national / single-geo collectors.

Used by collector stamps (``raw['country_code']``) and by country backfill
when location text alone cannot resolve a code.
"""

from __future__ import annotations

# connector_type → ISO2 stored on Job.country_code
SOURCE_DEFAULT_COUNTRY: dict[str, str] = {
    "arbetsformedlingen": "SE",
    "mpsv": "CZ",
    "mpsv_stream": "CZ",
    "mycareersfuture": "SG",
    "kalibrr": "PH",
    "wanted": "KR",
    "nav_arbeidsplassen": "NO",
    "nav_stilling_feed": "NO",
    "jobup": "CH",
    "tecnoempleo": "ES",
    "duunitori": "FI",
    "jobindex": "DK",
    "posao_hr": "HR",
    "dou_ua": "UA",
    "helloworld_rs": "RS",
    "instahyre": "IN",
    "wantedly": "JP",
    "nofluffjobs": "PL",
    "le_forem": "BE",
    "okemprego": "PT",
    "jobbank_ca": "CA",
    "viewjobs": "AU",
}
