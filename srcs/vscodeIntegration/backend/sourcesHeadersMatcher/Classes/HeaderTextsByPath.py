from __future__ import annotations

import os
from pathlib import Path
from typing import TypeAlias

from regexTools.getInclude import get_include
from utils import is_excluded


HeaderTextsByPath: TypeAlias = dict[str, str]


def getHeaderTexts(
    start_path: Path,
    excluded_paths: set[Path],
    header_extensions: set[str],
) -> HeaderTextsByPath:
    header_texts: HeaderTextsByPath = {}

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


def getIncludeSet(header_texts_by_path: HeaderTextsByPath) -> set[str]:
    include_set: set[str] = set()

    for header_text in header_texts_by_path.values():
        include_set.update(get_include(header_text))
    return include_set
