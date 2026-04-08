from __future__ import annotations

from Classes.Header.Header import Header
from Classes.Symbol.Symbol import Symbol


def append_proto_entries_to_header_map(
    headers: dict[str, Header],
    entry: Symbol,
    symbols: dict[str, Symbol],
) -> None:
    header_path = entry.header_path
    if header_path not in headers:
        headers[header_path] = Header(path=header_path)
    header = headers[header_path]
    header.append_proto_entry(entry)


def getHeaderMap(symbols: dict[str, Symbol]) -> dict[str, Header]:
    headers: dict[str, Header] = {}
    for entry in symbols.values():
        append_proto_entries_to_header_map(headers, entry, symbols)
    return headers
