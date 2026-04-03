from __future__ import annotations

import argparse
import os
from pathlib import Path

from Classes.resolved_proto import ResolvedProto
from Classes.traversal_result import TraversalResult
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from printer import format_stringified_headers
from protoImplementationMatcher import build_proto_map
from recurence import setRecurence
from resolveProto import resolveProto
from stringify import stringify_headers
from utils import _is_excluded, _normalize_excluded_paths


C_SOURCE_EXTENSIONS = {".c"}
CPP_SOURCE_EXTENSIONS = {".cc", ".cpp"}
RECURENCE_LIMIT = 0


def merge_header_map(global_header_map: GeneratedHeaders, file_header_map: GeneratedHeaders) -> None:
    for proto_name, entries in file_header_map.items():
        global_header_map.setdefault(proto_name, []).extend(entries)


def collect_sources(
    start_path: Path,
    excluded_paths: set[Path],
    source_extensions: set[str],
    proto: ResolvedProto,
) -> tuple[SourceTextsByPath, GeneratedHeaders]:
    source_texts: SourceTextsByPath = {}
    generated_headers: GeneratedHeaders = {}

    for current_root, dir_names, file_names in os.walk(start_path):
        current_path = Path(current_root).resolve()
        if _is_excluded(current_path, excluded_paths):
            dir_names[:] = []
            continue

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not _is_excluded(current_path / dir_name, excluded_paths)
        ]

        for file_name in file_names:
            file_path = current_path / file_name
            if file_path.suffix.lower() in source_extensions:
                resolved_path = str(file_path.resolve())
                source_text = file_path.read_text(encoding="utf-8", errors="ignore")
                source_texts[resolved_path] = source_text
                file_header_map = build_proto_map(resolved_path, proto, source_text)
                merge_header_map(generated_headers, file_header_map)

    return source_texts, generated_headers


def traverse_file_system(startPath: str, excludedFolderPath: list[str]) -> TraversalResult:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath)
    source_extensions = C_SOURCE_EXTENSIONS | CPP_SOURCE_EXTENSIONS
    proto = resolveProto(startPath, source_extensions, excludedFolderPath)
    source_texts_by_path, generated_headers = collect_sources(
        start_path,
        excluded_paths,
        source_extensions,
        proto,
    )

    return TraversalResult(
        proto=proto,
        generated_headers=generated_headers,
        source_texts_by_path=source_texts_by_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("startPath")
    parser.add_argument("excludedFolderPath", nargs="*")
    args = parser.parse_args()
    startPath = args.startPath
    excludedFolderPath = args.excludedFolderPath

    traversal_result = traverse_file_system(startPath, excludedFolderPath)
    setRecurence(traversal_result.generated_headers, traversal_result.source_texts_by_path)

    stringified_headers = stringify_headers(traversal_result.generated_headers)
    print(format_stringified_headers(stringified_headers))


if __name__ == "__main__":
    main()
