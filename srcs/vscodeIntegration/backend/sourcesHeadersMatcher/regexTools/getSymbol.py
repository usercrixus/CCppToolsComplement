from __future__ import annotations

import re

from Classes.ResolvedProto import ResolvedProto


def extract_name(statement: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(statement)
    if match is None:
        return None
    return match.group(1)


def extract_struct_name(statement: str) -> str | None:
    return extract_name(statement, ResolvedProto.STRUCT_NAME_RE)


def extract_typedef_name(statement: str) -> str | None:
    using_name = extract_name(statement, ResolvedProto.USING_NAME_RE)
    if using_name is not None:
        return using_name

    return extract_name(statement, re.compile(r"\b([A-Za-z_]\w*)\s*;\s*$", re.DOTALL))


def extract_symbol_name(
    statement: str,
    primary_pattern: re.Pattern[str],
    fallback_pattern: re.Pattern[str] | None = None,
) -> str | None:
    symbol_name = extract_name(statement, primary_pattern)
    if symbol_name is not None or fallback_pattern is None:
        return symbol_name
    return extract_name(statement, fallback_pattern)
