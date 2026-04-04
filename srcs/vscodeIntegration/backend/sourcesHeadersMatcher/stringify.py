from __future__ import annotations

import os
from pathlib import Path
from Classes.proto_match import ProtoMatch
from Classes.render_job import RenderJob
from Classes.type_aliases import HeaderMap, IncludeMap
from generatedHeaders import GeneratedHeaders


def _append_unique(target_list: list[str], seen_values: set[str], value: str) -> None:
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _header_path_from_source(source_path: str) -> str:
    return str(Path(source_path).with_suffix(".h"))


def _entry_recurence_score(entry: ProtoMatch) -> int:
    return sum(entry.recurence.values())


def _target_headers_for_proto(entries: list[ProtoMatch]) -> list[str]:
    if not entries:
        return []
    proto_type = entries[0].proto_type
    if proto_type == "function":
        return [_header_path_from_source(entry.source) for entry in entries]

    if proto_type in {"macro", "struct", "typedef", "class"}:
        best_entry = max(entries, key=_entry_recurence_score)
        return [_header_path_from_source(best_entry.source)]

    return []


def _append_proto_entries_to_header_map(
    header_map: HeaderMap,
    seen_header_values: dict[str, set[str]],
    entries: list[ProtoMatch],
) -> None:
    if not entries:
        return

    proto_type = entries[0].proto_type
    if proto_type == "function":
        for entry in entries:
            header_path = _header_path_from_source(entry.source)
            header_map.setdefault(header_path, [])
            seen_header_values.setdefault(header_path, set())
            _append_unique(header_map[header_path], seen_header_values[header_path], entry.declaration)
        return

    target_headers = _target_headers_for_proto(entries)
    for header_path in target_headers:
        header_map.setdefault(header_path, [])
        seen_header_values.setdefault(header_path, set())
        for entry in entries:
            _append_unique(header_map[header_path], seen_header_values[header_path], entry.declaration)


def _build_header_map(generated_headers: GeneratedHeaders) -> HeaderMap:
    header_map: HeaderMap = {}
    seen_header_values: dict[str, set[str]] = {}

    for entries in generated_headers.values():
        _append_proto_entries_to_header_map(header_map, seen_header_values, entries)

    return header_map


def _set_entry_header_paths(generated_headers: GeneratedHeaders) -> None:
    for entries in generated_headers.values():
        target_headers = _target_headers_for_proto(entries)
        if not target_headers:
            continue

        header_path = target_headers[0]
        for entry in entries:
            entry.header_path = header_path


def _render_header_content(protos: list[str]) -> str:
    body = "\n".join(protos)
    if body:
        body = f"{body}\n"

    return f"#pragma once\n\n{body}"


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


def _build_source_include_map(generated_headers: GeneratedHeaders) -> IncludeMap:
    include_map: IncludeMap = {}

    for entries in generated_headers.values():
        for entry in entries:
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


def _build_source_jobs(generated_headers: GeneratedHeaders) -> list[RenderJob]:
    source_jobs: list[RenderJob] = []
    include_map = _build_source_include_map(generated_headers)

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


def stringify_headers(generated_headers: GeneratedHeaders) -> list[RenderJob]:
    _set_entry_header_paths(generated_headers)
    header_map = _build_header_map(generated_headers)
    header_jobs = [
        RenderJob(path=header_path, string=_render_header_content(protos))
        for header_path, protos in sorted(header_map.items())
    ]
    source_jobs = _build_source_jobs(generated_headers)

    return header_jobs + source_jobs
