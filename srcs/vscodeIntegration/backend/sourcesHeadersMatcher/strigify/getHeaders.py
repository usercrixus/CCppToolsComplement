from __future__ import annotations

import re
from pathlib import Path

from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch
from Classes.ResolvedProto import ResolvedProto
from Classes.TypeAliases import Headers, Symbols


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


def _header_symbol_map(symbols: Symbols) -> dict[str, set[str]]:
    symbol_to_headers: dict[str, set[str]] = {}
    for symbol_name, entry in symbols.items():
        if entry.header_path:
            symbol_to_headers.setdefault(symbol_name, set()).add(str(Path(entry.header_path).resolve()))
    return symbol_to_headers


def set_header_includes(headers: Headers, symbols: Symbols) -> None:
    symbol_to_headers = _header_symbol_map(symbols)

    for header in headers.values():
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
    headers: Headers,
    seen_header_values: dict[str, set[str]],
    entry: ProtoMatch,
) -> None:
    proto_type = entry.proto_type
    header_path = entry.header_path
    if not header_path:
        return

    if header_path not in headers:
        headers[header_path] = Header(path=header_path)
    seen_values = seen_header_values.setdefault(header_path, set())
    header = headers[header_path]

    if proto_type == "function":
        _append_unique(header.functions, seen_values, entry.declaration)
    elif proto_type == "struct":
        _append_struct_entry(header, seen_values, entry)
    elif proto_type == "typedef":
        _append_typedef_entry(header, seen_values, entry)
    else:
        target_bucket = ResolvedProto.iter_proto_groups(header).get(proto_type, (None, None, None))[0]
        if target_bucket is not None:
            _append_unique(target_bucket, seen_values, entry.declaration)


def get_header_map(symbols: Symbols) -> Headers:
    headers: Headers = {}
    seen_header_values: dict[str, set[str]] = {}
    for entry in symbols.values():
        append_proto_entries_to_header_map(headers, seen_header_values, entry)
    return headers
