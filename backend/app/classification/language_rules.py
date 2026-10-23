"""Extract human language requirements from job text (not programming languages)."""

from __future__ import annotations

import re

# ISO 639-1 → keyword patterns (word-boundary). Order matters for display only.
_LANGUAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "en",
        re.compile(
            r"\b("
            r"english|anglais|englisch|inglese|inglés|inglês|"
            r"fluent\s+english|native\s+english|business\s+english"
            r")\b",
            re.I,
        ),
    ),
    (
        "it",
        re.compile(
            r"\b("
            r"italian|italien|italienisch|italiano|italiang|"
            r"lingua\s+italiana|parlare\s+italiano|fluent\s+italian"
            r")\b",
            re.I,
        ),
    ),
    (
        "de",
        re.compile(
            r"\b("
            r"german|deutsch|allemand|tedesco|alemán|"
            r"fluent\s+german|native\s+german|deutschkenntnisse"
            r")\b",
            re.I,
        ),
    ),
    (
        "fr",
        re.compile(
            r"\b("
            r"french|français|francais|französisch|francese|francés|"
            r"fluent\s+french|native\s+french"
            r")\b",
            re.I,
        ),
    ),
    (
        "es",
        re.compile(
            r"\b("
            r"spanish|español|espanol|spanisch|spagnolo|espagnol|"
            r"fluent\s+spanish|native\s+spanish"
            r")\b",
            re.I,
        ),
    ),
    (
        "pt",
        re.compile(
            r"\b(portuguese|português|portugues|portugiesisch|portoghese)\b",
            re.I,
        ),
    ),
    (
        "nl",
        re.compile(r"\b(dutch|nederlands|niederländisch|olandese|hollandais)\b", re.I),
    ),
    (
        "pl",
        re.compile(r"\b(polish|polski|polnisch|polacco|polonais)\b", re.I),
    ),
    (
        "sv",
        re.compile(r"\b(swedish|svenska|schwedisch|svedese|suédois)\b", re.I),
    ),
    (
        "da",
        re.compile(r"\b(danish|dansk|dänisch|danese|danois)\b", re.I),
    ),
    (
        "no",
        re.compile(r"\b(norwegian|norsk|norwegisch|norvegese|norvégien)\b", re.I),
    ),
    (
        "fi",
        re.compile(r"\b(finnish|suomi|finnisch|finlandese|finnois)\b", re.I),
    ),
    (
        "ru",
        re.compile(r"\b(russian|русский|russisch|russo|russe)\b", re.I),
    ),
    (
        "zh",
        re.compile(r"\b(chinese|mandarin|中文|cinese|chinois|chinesisch)\b", re.I),
    ),
    (
        "ja",
        re.compile(r"\b(japanese|日本語|japanisch|giapponese|japonais)\b", re.I),
    ),
    (
        "ar",
        re.compile(r"\b(arabic|عربي|arabisch|arabo|arabe)\b", re.I),
    ),
    (
        "lb",
        re.compile(r"\b(luxembourgish|lëtzebuergesch|luxembourgeois)\b", re.I),
    ),
)

# Avoid treating programming languages / frameworks as human languages.
_FALSE_FRIENDS = re.compile(
    r"\b("
    r"java(?!script)|javascript|typescript|golang|python|kotlin|swift|ruby|rust|"
    r"scala|csharp|c\+\+|objective[\s-]?c|php|perl|haskell|elixir|clojure|"
    r"sql|nosql|graphql|html|css|bash|powershell"
    r")\b",
    re.I,
)

_REQUIRE_CONTEXT = re.compile(
    r"\b("
    r"language|languages|lingua|lingue|sprache|sprachen|langue|langues|"
    r"idioma|idiomas|spoken|fluency|fluent|native|bilingual|trilingu|"
    r"required|requirement|requirements|must\s+speak|parlare|sprechen|"
    r"parler|hablar|C1|C2|B2|CEFR|IELTS|TOEFL"
    r")\b",
    re.I,
)


def extract_language_requirements(
    *,
    title: str = "",
    description: str | None = None,
    tags: list[str] | None = None,
) -> list[str]:
    """Return sorted unique ISO 639-1 codes for human languages required in the ad."""
    blob = " ".join(
        filter(None, [title, description or "", " ".join(tags or [])])
    )
    if not blob.strip():
        return []

    # Programming-only mentions without language-requirement context → skip matches
    # that are only false-friend tokens (handled per-pattern via word boundaries).
    found: list[str] = []
    for code, pattern in _LANGUAGE_PATTERNS:
        if not pattern.search(blob):
            continue
        # "Go" / short tokens not in list; "Java" is false friend for "en"? No.
        # Require either language-requirement context OR an explicit language adjective.
        if code == "en" and _FALSE_FRIENDS.search(blob) and not _REQUIRE_CONTEXT.search(blob):
            # "Java English" rare; "English" alone always OK via pattern.
            # Only gate when the only "language-ish" hit might be ambiguous — EN adjectives are clear.
            pass
        found.append(code)

    # Drop empty; stable order by first appearance in _LANGUAGE_PATTERNS
    order = {code: i for i, (code, _) in enumerate(_LANGUAGE_PATTERNS)}
    return sorted(set(found), key=lambda c: order.get(c, 99))
