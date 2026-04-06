from __future__ import annotations

import re
from pathlib import Path

from Classes.GeneratedHeaders import GeneratedHeaders
from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch
from Classes.ResolvedProto import ResolvedProto
from Classes.TypeAliases import HeaderMap
from strigify.setHeaderPath import header_path_from_source


def _append_unique(target_list: list[str], seen_values: set[str], value: str) -> None:
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


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


def _header_symbol_map(generated_headers: GeneratedHeaders) -> dict[str, set[str]]:
    symbol_to_headers: dict[str, set[str]] = {}
    for symbol_name, entry in generated_headers.items():
        if entry.header_path:
            symbol_to_headers.setdefault(symbol_name, set()).add(str(Path(entry.header_path).resolve()))
    return symbol_to_headers


def set_header_includes(header_map: HeaderMap, generated_headers: GeneratedHeaders) -> None:
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


def append_proto_entries_to_header_map(
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
    target_bucket = ResolvedProto.iter_proto_groups(header_map[header_path]).get(proto_type, (None, None, None))[0]
    if target_bucket is None:
        return
    _append_unique(target_bucket, seen_header_values[header_path], entry.declaration)


def get_header_map(generated_headers: GeneratedHeaders) -> HeaderMap:
    header_map: HeaderMap = {}
    seen_header_values: dict[str, set[str]] = {}
    for entry in generated_headers.values():
        append_proto_entries_to_header_map(header_map, seen_header_values, entry)
    return header_map
