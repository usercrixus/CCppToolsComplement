from __future__ import annotations

from Classes.Header.HeaderMap import getHeaderMap
from Classes.Source.SourceMap import getSourceMap
from Classes.Symbol.Symbol import Symbol


def stringify(symbols: dict[str, Symbol]) -> list[dict[str, str]]:
    headers = getHeaderMap(symbols)
    sources = getSourceMap(symbols)
    header_jobs = [
        {"path": header.path, "string": header.toString()}
        for _, header in sorted(headers.items())
    ]
    source_jobs = [
        {"path": source.path, "string": source.toString()}
        for _, source in sorted(sources.items())
    ]

    return header_jobs + source_jobs
