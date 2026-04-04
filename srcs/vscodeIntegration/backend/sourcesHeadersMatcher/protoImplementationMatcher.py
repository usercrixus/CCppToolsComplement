from __future__ import annotations

import re
from pathlib import Path

from Classes.extracted_file_statements import ExtractedFileStatements
from Classes.proto_match import ProtoMatch
from Classes.resolved_proto import ResolvedProto
from generatedHeaders import GeneratedHeaders
from getSourceProto import (
    get_c_function_imp,
    get_cpp_class_imp,
    get_macro_proto,
    get_struct_imp,
    get_struct_proto,
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


def _find_matching_function_imp(proto: str, function_imps: list[str]) -> str | None:
    proto_name = _extract_name(proto, ResolvedProto.FUNCTION_NAME_RE)
    if proto_name is None:
        return None

    for function_imp in function_imps:
        if _extract_name(function_imp, ResolvedProto.FUNCTION_NAME_RE) == proto_name:
            return function_imp
    return None


def _find_matching_struct(proto: str, struct_statements: list[str]) -> str | None:
    proto_name = _extract_name(proto, ResolvedProto.STRUCT_NAME_RE)
    if proto_name is None:
        return None

    for struct_statement in struct_statements:
        if _extract_name(struct_statement, ResolvedProto.STRUCT_NAME_RE) == proto_name:
            return struct_statement
    return None


def _find_matching_class(proto: str, class_statements: list[str]) -> str | None:
    proto_name = _extract_name(proto, ResolvedProto.CLASS_NAME_RE)
    if proto_name is None:
        return None

    for class_statement in class_statements:
        if _extract_name(class_statement, ResolvedProto.CLASS_NAME_RE) == proto_name:
            return class_statement
    return None


def _find_matching_typedef(proto: str, typedef_statements: list[str]) -> str | None:
    proto_name = _extract_symbol_name(proto, ResolvedProto.USING_NAME_RE, ResolvedProto.TYPEDEF_NAME_RE)
    if proto_name is None:
        return None

    for typedef_statement in typedef_statements:
        if _extract_symbol_name(typedef_statement, ResolvedProto.USING_NAME_RE, ResolvedProto.TYPEDEF_NAME_RE) == proto_name:
            return typedef_statement
    return None


def _match_proto(proto_type: str, proto: str, extracted_file_statements: ExtractedFileStatements) -> str | None:
    if proto_type == "class":
        return _find_matching_class(proto, extracted_file_statements.classes)
    if proto_type == "function":
        return _find_matching_function_imp(proto, extracted_file_statements.function_implementations)
    if proto_type == "macro":
        return proto if proto in extracted_file_statements.macros else None
    if proto_type == "struct":
        return _find_matching_struct(proto, extracted_file_statements.structs)
    if proto_type == "typedef":
        return _find_matching_typedef(proto, extracted_file_statements.typedefs)
    return None


def extract_file_statements(file_text: str) -> ExtractedFileStatements:
    return ExtractedFileStatements(
        classes=get_cpp_class_imp(file_text),
        function_implementations=get_c_function_imp(file_text),
        macros=get_macro_proto(file_text),
        structs=list(dict.fromkeys(get_struct_proto(file_text) + get_struct_imp(file_text))),
        typedefs=get_typedef_proto(file_text),
    )


def build_proto_map(
    file_path: str | Path,
    proto_groups: ResolvedProto,
    file_text: str,
) -> GeneratedHeaders:
    file_path = Path(file_path).expanduser().resolve()
    extracted_file_statements = extract_file_statements(file_text)
    result_map: GeneratedHeaders = {}
    for proto_type, protos, symbol_pattern, fallback_symbol_pattern in ResolvedProto.iter_proto_groups(proto_groups):
        for proto in protos:
            implementation = _match_proto(proto_type, proto, extracted_file_statements)
            if implementation:
                symbol_name = _extract_symbol_name(proto, symbol_pattern, fallback_symbol_pattern)
                if symbol_name is None:
                    continue
                entry = ProtoMatch(
                    declaration=proto,
                    symbol_name=symbol_name,
                    proto_type=proto_type,
                    implementation=implementation,
                    source=str(file_path),
                    recurence={},
                )
                result_map.setdefault(symbol_name, []).append(entry)
    return result_map
