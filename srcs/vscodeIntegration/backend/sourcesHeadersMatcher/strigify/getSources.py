from __future__ import annotations

from pathlib import Path

from Classes.RenderJob import RenderJob
from Classes.Source import Source
from Classes.TypeAliases import Symbols


def get_sources(symbols: Symbols) -> dict[str, Source]:
    sources: dict[str, Source] = {}

    for entry in symbols.values():
        source_path = str(Path(entry.source).resolve())
        source = sources.setdefault(source_path, Source(path=source_path))
        source.append_proto_entry(entry)

        header_path = entry.header_path
        if not header_path:
            continue

        resolved_header_path = str(Path(header_path).resolve())
        source.append_include(resolved_header_path)

        for recurence_source in entry.recurence:
            recurence_source = str(Path(recurence_source).resolve())
            recurence_source_entry = sources.setdefault(recurence_source, Source(path=recurence_source))
            recurence_source_entry.append_include(resolved_header_path)

    return sources


def get_source_jobs(symbols: Symbols) -> list[RenderJob]:
    source_jobs: list[RenderJob] = []
    sources = get_sources(symbols)
    for source_path, source in sorted(sources.items()):
        source_jobs.append(RenderJob(path=source.path, string=source.toString()))

    return source_jobs
