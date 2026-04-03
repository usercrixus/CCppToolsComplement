from __future__ import annotations

import re
from pathlib import Path

from Classes.extracted_file_statements import ExtractedFileStatements
from Classes.proto_match import ProtoMatch
from Classes.recurrence import Recurrence
from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from getSourceProto import (
    get_c_function_proto,
    get_c_function_imp,
    get_cpp_class_imp,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_forward_decl,
    get_struct_imp,
    get_struct_proto,
    get_typedef_proto,
)
FUNCTION_NAME_RE = re.compile(r"([A-Za-z_]\w*)\s*\(")
MACRO_NAME_RE = re.compile(r"#\s*define\s+([A-Za-z_]\w*)")
CLASS_NAME_RE = re.compile(r"\bclass\s+([A-Za-z_]\w*)")
STRUCT_NAME_RE = re.compile(r"\bstruct\s+([A-Za-z_]\w*)")
TYPEDEF_NAME_RE = re.compile(r"\btypedef\b[\s\S]*?\b([A-Za-z_]\w*)\s*;")
USING_NAME_RE = re.compile(r"\busing\s+([A-Za-z_]\w*)\s*=")


def _extract_name(statement: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(statement)
    if match is None:
        return None
    return match.group(1)


def _extract_typedef_name(statement: str) -> str | None:
    using_name = _extract_name(statement, USING_NAME_RE)
    if using_name is not None:
        return using_name
    return _extract_name(statement, TYPEDEF_NAME_RE)


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
    file_path: Path,
    file_text: str,
    symbol_name: str | None,
    source_texts_by_path: SourceTextsByPath,
) -> list[Recurrence]:
    recurence: list[Recurrence] = []
    all_source_texts = dict(source_texts_by_path)
    all_source_texts.setdefault(str(file_path), file_text)
    implementation_source = str(file_path)

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

    return [Recurrence(source=str(file_path), times=_count_symbol_usage(_strip_non_usage_statements(file_text), symbol_name))]


def _find_matching_function_imp(proto: str, function_imps: list[str]) -> str | None:
    proto_name = _extract_name(proto, FUNCTION_NAME_RE)
    if proto_name is None:
        return None

    for function_imp in function_imps:
        if _extract_name(function_imp, FUNCTION_NAME_RE) == proto_name:
            return function_imp
    return None


def _find_matching_struct(proto: str, struct_statements: list[str]) -> str | None:
    proto_name = _extract_name(proto, STRUCT_NAME_RE)
    if proto_name is None:
        return None

    for struct_statement in struct_statements:
        if _extract_name(struct_statement, STRUCT_NAME_RE) == proto_name:
            return struct_statement
    return None


def _find_matching_class(proto: str, class_statements: list[str]) -> str | None:
    proto_name = _extract_name(proto, CLASS_NAME_RE)
    if proto_name is None:
        return None

    for class_statement in class_statements:
        if _extract_name(class_statement, CLASS_NAME_RE) == proto_name:
            return class_statement
    return None


def _find_matching_typedef(proto: str, typedef_statements: list[str]) -> str | None:
    proto_name = _extract_typedef_name(proto)
    if proto_name is None:
        return None

    for typedef_statement in typedef_statements:
        if _extract_typedef_name(typedef_statement) == proto_name:
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
    file_path: Path,
    proto_groups: ResolvedProto,
    file_text: str,
    source_texts_by_path: SourceTextsByPath | None = None,
) -> GeneratedHeaders:
    extracted_file_statements = extract_file_statements(file_text)
    result_map: GeneratedHeaders = {}
    source_texts_by_path = source_texts_by_path or {}

    for proto_type, protos in (
        ("class", proto_groups.classes),
        ("function", proto_groups.functions),
        ("macro", proto_groups.macros),
        ("struct", proto_groups.structs),
        ("typedef", proto_groups.typedefs),
    ):
        for proto in protos:
            implementation = _match_proto(proto_type, proto, extracted_file_statements)
            if implementation is None:
                continue

            if proto_type == "class":
                symbol_name = _extract_name(proto, CLASS_NAME_RE)
            elif proto_type == "function":
                symbol_name = _extract_name(proto, FUNCTION_NAME_RE)
            elif proto_type == "macro":
                symbol_name = _extract_name(proto, MACRO_NAME_RE)
            elif proto_type == "struct":
                symbol_name = _extract_name(proto, STRUCT_NAME_RE)
            else:
                symbol_name = _extract_typedef_name(proto)

            entry = ProtoMatch(
                implementation=implementation,
                source=str(file_path),
                recurence=_build_recurence(file_path, file_text, symbol_name, source_texts_by_path),
            )
            result_map.setdefault(proto, []).append(entry)

    return result_map
