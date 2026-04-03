from __future__ import annotations

import re

from Classes.recurrence import Recurrence
from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from getSourceProto import (
    get_c_function_imp,
    get_c_function_proto,
    get_cpp_class_imp,
    get_cpp_function_proto,
    get_struct_forward_decl,
    get_struct_imp,
    get_typedef_proto,
)


def _extract_name(statement: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(statement)
    if match is None:
        return None
    return match.group(1)


def _extract_symbol_name(
    statement: str,
    primary_pattern: re.Pattern[str],
    fallback_pattern: re.Pattern[str] | None = None,
) -> str | None:
    symbol_name = _extract_name(statement, primary_pattern)
    if symbol_name is not None or fallback_pattern is None:
        return symbol_name
    return _extract_name(statement, fallback_pattern)


def _count_symbol_usage(file_text: str, symbol_name: str | None) -> int:
    if not symbol_name:
        return 0
    return len(re.findall(rf"\b{re.escape(symbol_name)}\b", file_text))


def _remove_statements_from_text(file_text: str, statements: list[str]) -> str:
    updated_text = file_text
    for statement in statements:
        if not statement:
            continue
        updated_text = updated_text.replace(statement, "")
    return updated_text


def _strip_non_usage_statements(file_text: str) -> str:
    non_usage_statements = list(
        dict.fromkeys(
            get_c_function_proto(file_text)
            + get_cpp_function_proto(file_text)
            + get_c_function_imp(file_text)
            + get_struct_forward_decl(file_text)
            + get_struct_imp(file_text)
            + get_typedef_proto(file_text)
            + get_cpp_class_imp(file_text)
        )
    )
    return _remove_statements_from_text(file_text, non_usage_statements)


def _build_recurence(
    file_path: str,
    symbol_name: str | None,
    source_texts_by_path: SourceTextsByPath,
) -> list[Recurrence]:
    recurence: list[Recurrence] = []
    all_source_texts = dict(source_texts_by_path)
    implementation_source = str(file_path)
    file_text = all_source_texts.get(implementation_source, "")

    for source_path, source_text in all_source_texts.items():
        usage_text = _strip_non_usage_statements(source_text)
        times = _count_symbol_usage(usage_text, symbol_name)
        if str(source_path) == implementation_source:
            times = max(times, 0)
        if times <= 0:
            continue

        recurence.append(Recurrence(source=str(source_path), times=times))

    if recurence:
        return recurence

    return [Recurrence(source=implementation_source, times=_count_symbol_usage(_strip_non_usage_statements(file_text), symbol_name))]


def _symbol_name_from_proto(proto: str) -> str | None:
    for _, _, symbol_pattern, fallback_symbol_pattern in ResolvedProto.iter_proto_groups(ResolvedProto()):
        symbol_name = _extract_symbol_name(proto, symbol_pattern, fallback_symbol_pattern)
        if symbol_name is not None:
            return symbol_name
    return None


def setRecurence(generated_headers: GeneratedHeaders, source_texts_by_path: SourceTextsByPath) -> None:
    for proto, entries in generated_headers.items():
        symbol_name = _symbol_name_from_proto(proto)
        for entry in entries:
            entry.recurence = _build_recurence(entry.source, symbol_name, source_texts_by_path)
