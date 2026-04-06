from __future__ import annotations

from regexTools.common import INCLUDE_RE, extract_matches


def get_include(text: str | None) -> list[str]:
    return extract_matches(text, INCLUDE_RE)
