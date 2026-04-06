from __future__ import annotations

from Classes.RenderJob import RenderJob
from Classes.TypeAliases import Symbols
from strigify.getHeaders import get_header_map
from strigify.getSources import get_source_jobs
from strigify.setHeaderPath import set_entry_header_paths


def stringify_headers(symbols: Symbols) -> list[RenderJob]:
    set_entry_header_paths(symbols)
    headers = get_header_map(symbols)
    header_jobs = [
        RenderJob(path=header.path, string=header.toString())
        for _, header in sorted(headers.items())
    ]
    source_jobs = get_source_jobs(symbols)

    return header_jobs + source_jobs
