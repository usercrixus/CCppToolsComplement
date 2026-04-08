from __future__ import annotations

from pathlib import Path

from Classes.Source.Source import Source
from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.Symbol import Symbol


def getSourceMap(symbols: dict[str, Symbol]) -> dict[str, Source]:
    sources: dict[str, Source] = {}

    for entry in symbols.values():
        if not isinstance(entry, FunctionSymbol):
            continue

        source_path = str(Path(entry.source).resolve())
        source = sources.setdefault(source_path, Source(path=source_path))
        source.append_proto_entry(entry)

        header_path = entry.header_path
        if not header_path:
            continue

        resolved_header_path = str(Path(header_path).resolve())
        source.append_include(resolved_header_path)

    return sources
