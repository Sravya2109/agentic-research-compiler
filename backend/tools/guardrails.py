from __future__ import annotations

import re


def validate_query(query: str) -> tuple[bool, str]:
    normalized_query = query.strip()

    if len(normalized_query) < 10:
        return False, "Query is too short. Please provide more detail."

    if len(normalized_query) > 500:
        return False, "Query is too long. Please keep it under 500 characters."

    blocked_phrases = (
        "illegal",
        "hack into",
        "weapons",
        "personal information about",
        "how to make",
    )

    lowered_query = normalized_query.lower()
    if any(phrase in lowered_query for phrase in blocked_phrases):
        return False, "This query touches restricted content and cannot be processed."

    return True, "ok"


def check_report_for_hallucinations(
    report_sections: list[dict],
    source_urls: list[str],
) -> list[str]:
    flags: list[str] = []

    for index, section in enumerate(report_sections, start=1):
        confidence = section.get("confidence", 0)
        if confidence < 0.5:
            flags.append(f"Section {index} has low confidence ({confidence}).")

        citations = section.get("citations", [])
        if not citations:
            flags.append(f"Section {index} has no citations.")

    return flags


def sanitize_output(text: str) -> str:
    cleaned_text = re.sub(r"<\|.*?\|>", "", text)
    cleaned_lines = [line for line in cleaned_text.splitlines() if not line.lstrip().startswith("SYSTEM:")]
    return "\n".join(cleaned_lines)
