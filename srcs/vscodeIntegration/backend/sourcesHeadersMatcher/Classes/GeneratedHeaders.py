from __future__ import annotations

import os
from pathlib import Path
from typing import TypeAlias

from Classes.ProtoMatch import ProtoMatch
from Classes.ResolvedProto import ResolvedProto
from Classes.SourceTextsByPath import SourceTextsByPath
from utils import is_excluded


GeneratedHeaders: TypeAlias = dict[str, ProtoMatch]


def merge_header_map(global_header_map: GeneratedHeaders, file_header_map: GeneratedHeaders) -> None:
    global_header_map.update(file_header_map)


def process_source_file(
    file_path: Path,
    proto: ResolvedProto,
    source_texts: SourceTextsByPath,
    generated_headers: GeneratedHeaders,
) -> None:
    from protoImplementationMatcher import build_proto_map

    resolved_path = str(file_path.resolve())
    source_text = file_path.read_text(encoding="utf-8", errors="ignore")
    source_texts[resolved_path] = source_text
    file_header_map = build_proto_map(resolved_path, proto, source_text)
    merge_header_map(generated_headers, file_header_map)


def getGeneratedHeaders(
    start_path: Path,
    excluded_paths: set[Path],
    source_extensions: set[str],
    protos: ResolvedProto,
) -> GeneratedHeaders:
    generated_headers: GeneratedHeaders = {}

    for current_root, dir_names, file_names in os.walk(start_path):
        current_path = Path(current_root).resolve()
        if is_excluded(current_path, excluded_paths):
            dir_names[:] = []
            continue

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not is_excluded(current_path / dir_name, excluded_paths)
        ]

        for file_name in file_names:
            file_path = current_path / file_name
            if file_path.suffix.lower() in source_extensions:
                process_source_file(file_path, protos, {}, generated_headers)

    return generated_headers
