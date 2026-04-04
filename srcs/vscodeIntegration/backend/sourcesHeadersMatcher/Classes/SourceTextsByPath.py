from __future__ import annotations

import os
from pathlib import Path
from typing import TypeAlias

from utils import is_excluded


SourceTextsByPath: TypeAlias = dict[str, str]


def getSourceTexts(
    start_path: Path,
    excluded_paths: set[Path],
    source_extensions: set[str],
) -> SourceTextsByPath:
    source_texts: SourceTextsByPath = {}

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
                resolved_path = str(file_path.resolve())
                source_texts[resolved_path] = file_path.read_text(encoding="utf-8", errors="ignore")
    return source_texts
