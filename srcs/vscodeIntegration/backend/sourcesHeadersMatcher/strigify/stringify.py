from __future__ import annotations

import os
from pathlib import Path
from Classes.RenderJob import RenderJob
from Classes.TypeAliases import IncludeMap, Symbols
from strigify.getHeaders import get_header_map, set_header_includes
from strigify.setHeaderPath import set_entry_header_paths


def _existing_include_lines(file_text: str) -> set[str]:
    return {line.strip() for line in file_text.splitlines() if line.strip().startswith("#include ")}


def _string_with_inserted_include(file_text: str, include_line: str) -> str:
    if include_line in _existing_include_lines(file_text):
        return file_text

    lines = file_text.splitlines()
    insert_index = 0
    while insert_index < len(lines) and lines[insert_index].strip().startswith("#include "):
        insert_index += 1

    updated_lines = lines[:insert_index] + [include_line] + lines[insert_index:]
    return "\n".join(updated_lines) + "\n"


def _build_source_include_map(symbols: Symbols) -> IncludeMap:
    include_map: IncludeMap = {}

    for entry in symbols.values():
        header_path = entry.header_path
        if not header_path:
            continue

        implementation_source = str(Path(entry.source).resolve())
        resolved_header_path = str(Path(header_path).resolve())
        include_map.setdefault(implementation_source, set()).add(resolved_header_path)

        for recurence_source in entry.recurence:
            recurence_source = str(Path(recurence_source).resolve())
            include_map.setdefault(recurence_source, set()).add(resolved_header_path)

    return include_map


def _build_source_jobs(symbols: Symbols) -> list[RenderJob]:
    source_jobs: list[RenderJob] = []
    include_map = _build_source_include_map(symbols)

    for source_path, header_paths in sorted(include_map.items()):
        source_file = Path(source_path)
        source_text = source_file.read_text(encoding="utf-8", errors="ignore")

        for header_path in sorted(header_paths):
            include_path = os.path.relpath(
                Path(header_path).resolve(),
                source_file.resolve().parent,
            )
            include_line = f'#include "{Path(include_path).as_posix()}"'
            source_text = _string_with_inserted_include(source_text, include_line)

        source_jobs.append(RenderJob(path=source_path, string=source_text))

    return source_jobs


def stringify_headers(symbols: Symbols) -> list[RenderJob]:
    set_entry_header_paths(symbols)
    headers = get_header_map(symbols)
    set_header_includes(headers, symbols)
    header_jobs = [
        RenderJob(path=header.path, string=header.toString())
        for _, header in sorted(headers.items())
    ]
    source_jobs = _build_source_jobs(symbols)

    return header_jobs + source_jobs
