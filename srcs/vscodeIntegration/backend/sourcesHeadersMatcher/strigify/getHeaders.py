from __future__ import annotations

from pathlib import Path

from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch
from Classes.TypeAliases import Headers, Symbols
from strigify.setHeaderPath import header_path_from_source


def push_include(header: Header, include_path: str) -> None:
    resolved_include_path = str(Path(include_path).resolve())
    if resolved_include_path != str(Path(header.path).resolve()):
        header.includes.add(resolved_include_path)


def set_include(
    headers: Headers,
    symbols: Symbols,
) -> None:
    for header_path, header in headers.items():
        for symbol in symbols.values():
            if header_path in symbol.recurence and symbol.header_path:
                push_include(header, symbol.header_path)


def append_proto_entries_to_header_map(
    headers: Headers,
    entry: ProtoMatch,
    symbols: Symbols,
) -> None:
    header_path = entry.header_path
    if header_path not in headers:
        headers[header_path] = Header(path=header_path)
    header = headers[header_path]
    header.append_proto_entry(entry)


def get_header_map(symbols: Symbols) -> Headers:
    headers: Headers = {}
    for entry in symbols.values():
        append_proto_entries_to_header_map(headers, entry, symbols)
    return headers
