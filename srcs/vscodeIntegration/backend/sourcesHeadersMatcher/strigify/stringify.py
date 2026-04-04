from __future__ import annotations

import os
import re
from pathlib import Path
from Classes.GeneratedHeaders import GeneratedHeaders
from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch
from Classes.RenderJob import RenderJob
from Classes.TypeAliases import HeaderMap, IncludeMap
from strigify.setHeaderPath import header_path_from_source, set_entry_header_paths


def _append_unique(target_list: list[str], seen_values: set[str], value: str) -> None:
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _header_bucket(header: Header, proto_type: str) -> list[str] | None:
    if proto_type == "function":
        return header.functions
    if proto_type == "macro":
        return header.macros
    if proto_type == "struct":
        return header.structs
    if proto_type == "typedef":
        return header.typedefs
    if proto_type == "class":
        return header.classes
    return None


def _append_struct_entry(header: Header, seen_values: set[str], entry: ProtoMatch) -> None:
    struct_name_match = re.search(r"\bstruct\s+([A-Za-z_]\w*)", entry.declaration)
    if "{" in entry.declaration and struct_name_match is not None:
        _append_unique(header.struct_declarations, seen_values, f"struct {struct_name_match.group(1)};")
        _append_unique(header.structs, seen_values, entry.implementation)
        return

    _append_unique(header.struct_declarations, seen_values, entry.declaration)


def _append_typedef_entry(header: Header, seen_values: set[str], entry: ProtoMatch) -> None:
    typedef_name_match = re.search(r"\b([A-Za-z_]\w*)\s*;\s*$", entry.declaration, re.DOTALL)
    struct_name_match = re.search(r"\bstruct\s+([A-Za-z_]\w*)", entry.declaration)
    if "{" in entry.declaration and typedef_name_match is not None and struct_name_match is not None:
        _append_unique(
            header.typedef_declarations,
            seen_values,
            f"typedef struct {struct_name_match.group(1)} {typedef_name_match.group(1)};",
        )
        _append_unique(header.typedefs, seen_values, entry.implementation)
        return

    _append_unique(header.typedef_declarations, seen_values, entry.declaration)


def _append_proto_entries_to_header_map(
    header_map: HeaderMap,
    seen_header_values: dict[str, set[str]],
    entry: ProtoMatch,
) -> None:
    proto_type = entry.proto_type
    if proto_type == "function":
        header_path = header_path_from_source(entry.source)
        if header_path not in header_map:
            header_map[header_path] = Header(path=header_path)
        seen_header_values.setdefault(header_path, set())
        _append_unique(header_map[header_path].functions, seen_header_values[header_path], entry.declaration)
        return

    header_path = entry.header_path
    if not header_path:
        return
    if header_path not in header_map:
        header_map[header_path] = Header(path=header_path)
    seen_header_values.setdefault(header_path, set())
    if proto_type == "struct":
        _append_struct_entry(header_map[header_path], seen_header_values[header_path], entry)
        return
    if proto_type == "typedef":
        _append_typedef_entry(header_map[header_path], seen_header_values[header_path], entry)
        return
    target_bucket = _header_bucket(header_map[header_path], proto_type)
    if target_bucket is None:
        return
    _append_unique(target_bucket, seen_header_values[header_path], entry.declaration)


def _build_header_map(generated_headers: GeneratedHeaders) -> HeaderMap:
    header_map: HeaderMap = {}
    seen_header_values: dict[str, set[str]] = {}

    for entry in generated_headers.values():
        _append_proto_entries_to_header_map(header_map, seen_header_values, entry)

    return header_map


def _header_symbol_map(generated_headers: GeneratedHeaders) -> dict[str, set[str]]:
    symbol_to_headers: dict[str, set[str]] = {}
    for symbol_name, entry in generated_headers.items():
        if entry.header_path:
            symbol_to_headers.setdefault(symbol_name, set()).add(str(Path(entry.header_path).resolve()))
    return symbol_to_headers


def _set_header_includes(header_map: HeaderMap, generated_headers: GeneratedHeaders) -> None:
    symbol_to_headers = _header_symbol_map(generated_headers)

    for header in header_map.values():
        current_header_path = str(Path(header.path).resolve())
        for declaration in header.declarations():
            for symbol_name, target_headers in symbol_to_headers.items():
                if current_header_path in target_headers:
                    continue
                if re.search(rf"\b{re.escape(symbol_name)}\b", declaration) is None:
                    continue
                for target_header in target_headers:
                    if target_header != current_header_path:
                        header.includes.add(target_header)


def _existing_include_lines(file_text: str) -> set[str]:
    return {line.strip() for line in file_text.splitlines() if line.strip().startswith("#include ")}


def _string_with_inserted_include(file_text: str, include_line: str) -> str:
    if include_line in _existing_include_lines(file_text):
        return file_text

    lines = file_text.splitlines()
    insert_index = 0
    while insert_index < len(lines) and lines[insert_index].strip().startswith("#include "):
        insert_index += 1

    updated_lines = lines[:insert_index] + [include_line] + lines[insert_index:]
    return "\n".join(updated_lines) + "\n"


def _build_source_include_map(generated_headers: GeneratedHeaders) -> IncludeMap:
    include_map: IncludeMap = {}

    for entry in generated_headers.values():
        header_path = entry.header_path
        if not header_path:
            continue

        implementation_source = str(Path(entry.source).resolve())
        resolved_header_path = str(Path(header_path).resolve())
        include_map.setdefault(implementation_source, set()).add(resolved_header_path)

        for recurence_source in entry.recurence:
            recurence_source = str(Path(recurence_source).resolve())
            include_map.setdefault(recurence_source, set()).add(resolved_header_path)

    return include_map


def _build_source_jobs(generated_headers: GeneratedHeaders) -> list[RenderJob]:
    source_jobs: list[RenderJob] = []
    include_map = _build_source_include_map(generated_headers)

    for source_path, header_paths in sorted(include_map.items()):
        source_file = Path(source_path)
        source_text = source_file.read_text(encoding="utf-8", errors="ignore")

        for header_path in sorted(header_paths):
            include_path = os.path.relpath(
                Path(header_path).resolve(),
                source_file.resolve().parent,
            )
            include_line = f'#include "{Path(include_path).as_posix()}"'
            source_text = _string_with_inserted_include(source_text, include_line)

        source_jobs.append(RenderJob(path=source_path, string=source_text))

    return source_jobs


def stringify_headers(generated_headers: GeneratedHeaders) -> list[RenderJob]:
    set_entry_header_paths(generated_headers)
    header_map = _build_header_map(generated_headers)
    _set_header_includes(header_map, generated_headers)
    header_jobs = [
        RenderJob(path=header.path, string=header.toString())
        for _, header in sorted(header_map.items())
    ]
    source_jobs = _build_source_jobs(generated_headers)

    return header_jobs + source_jobs
