from __future__ import annotations

from Classes.RenderJob import RenderJob
from Classes.TypeAliases import Symbols
from strigify.getHeaders import get_header_map
from strigify.getSources import get_sources
from strigify.setHeaderPath import set_entry_header_paths


def stringify_headers(symbols: Symbols) -> list[RenderJob]:
    set_entry_header_paths(symbols)
    headers = get_header_map(symbols)
    sources = get_sources(symbols)
    header_jobs = [
        RenderJob(path=header.path, string=header.toString())
        for _, header in sorted(headers.items())
    ]
    source_jobs = [
        RenderJob(path=source.path, string=source.toString())
        for _, source in sorted(sources.items())
    ]

    return header_jobs + source_jobs
