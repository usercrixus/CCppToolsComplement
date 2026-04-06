from __future__ import annotations

import re

from regexTools.common import (
    CLASS_IMP_RE,
    STRUCT_BLOCK_START_RE,
    extract_macro_names,
    extract_matches,
    extract_multiline_statements,
)
from regexTools.getProto import get_typedef_proto


FUNCTION_IMP_START_RE = re.compile(
    r"^\s*(?:extern\s+)?[\w:<>\~\*&,\s]+?[A-Za-z_]\w*(?:::\w+)*\s*\([^;{}]*\)\s*(?:const\s*)?$"
)


def _extract_function_implementations(text: str | None) -> list[str]:
    if text is None:
        return []

    statements = []
    lines = text.splitlines()
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        stripped_line = raw_line.strip()
        if not FUNCTION_IMP_START_RE.match(stripped_line):
            line_index += 1
            continue
        if stripped_line.endswith(";"):
            line_index += 1
            continue

        statement_lines = [raw_line.rstrip()]
        brace_depth = raw_line.count("{") - raw_line.count("}")

        while brace_depth <= 0:
            line_index += 1
            if line_index >= len(lines):
                break
            next_line = lines[line_index]
            statement_lines.append(next_line.rstrip())
            brace_depth += next_line.count("{") - next_line.count("}")

        while brace_depth > 0:
            line_index += 1
            if line_index >= len(lines):
                break
            next_line = lines[line_index]
            statement_lines.append(next_line.rstrip())
            brace_depth += next_line.count("{") - next_line.count("}")

        statement = "\n".join(statement_lines).strip()
        if statement:
            statements.append(statement)

        line_index += 1

    return statements


def get_c_function_imp(text: str | None) -> list[str]:
    return _extract_function_implementations(text)


def get_cpp_function_imp(text: str | None) -> list[str]:
    return _extract_function_implementations(text)


def get_cpp_class_imp(text: str | None) -> list[str]:
    return extract_matches(text, CLASS_IMP_RE)


def get_macro_imp(text: str | None) -> list[str]:
    return extract_macro_names(text)


def get_struct_imp(text: str | None) -> list[str]:
    return extract_multiline_statements(text, STRUCT_BLOCK_START_RE)


def get_typedef_imp(text: str | None) -> list[str]:
    return get_typedef_proto(text)
