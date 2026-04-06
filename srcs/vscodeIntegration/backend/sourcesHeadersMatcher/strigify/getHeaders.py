from __future__ import annotations

import re
from pathlib import Path

from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch
from Classes.TypeAliases import Headers, Symbols


def header_symbol_map(symbols: Symbols) -> dict[str, set[str]]:
    symbol_to_headers: dict[str, set[str]] = {}
    for symbol_name, entry in symbols.items():
        if entry.header_path:
            symbol_to_headers.setdefault(symbol_name, set()).add(str(Path(entry.header_path).resolve()))
    return symbol_to_headers


def set_header_includes(headers: Headers, symbols: Symbols) -> None:
    symbol_to_headers = header_symbol_map(symbols)

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
    entry: ProtoMatch,
) -> None:
    header_path = entry.header_path
    if header_path not in headers:
        headers[header_path] = Header(path=header_path)
    header = headers[header_path]
    header.append_proto_entry(entry)


def get_header_map(symbols: Symbols) -> Headers:
    headers: Headers = {}
    for entry in symbols.values():
        append_proto_entries_to_header_map(headers, entry)
    return headers
