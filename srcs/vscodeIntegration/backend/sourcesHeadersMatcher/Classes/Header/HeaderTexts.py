from __future__ import annotations

import os
from pathlib import Path

from regexTools.getInclude import get_include
from utils import is_excluded


def getHeaderTexts(
    start_path: Path,
    excluded_paths: set[Path],
    header_extensions: set[str],
) -> dict[str, str]:
    header_texts: dict[str, str] = {}

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
            if file_path.suffix.lower() in header_extensions:
                resolved_path = str(file_path.resolve())
                header_texts[resolved_path] = file_path.read_text(encoding="utf-8", errors="ignore")
    return header_texts


def _resolve_include(file_path: str, include: str) -> str:
    if include.startswith("<") and include.endswith(">"):
        return include
    if include.startswith('"') and include.endswith('"'):
        include_path = include[1:-1]
        return str((Path(file_path).resolve().parent / include_path).resolve())
    return include


def getIncludeSet(header_texts_by_path: dict[str, str]) -> set[str]:
    include_set: set[str] = set()

    for file_path, header_text in header_texts_by_path.items():
        include_set.update(
            _resolve_include(file_path, include)
            for include in get_include(header_text)
        )
    return include_set
