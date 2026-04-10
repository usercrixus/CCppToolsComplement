from __future__ import annotations

import os
from pathlib import Path

from regexTools.common import MAIN_FUNCTION_RE
from utils import is_excluded


def get_mains_source_paths(
    start_path: Path,
    excluded_paths: set[Path],
    source_extensions: tuple[str, ...] | set[str],
) -> set[Path]:
    main_source_paths: set[Path] = set()

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
            if file_path.suffix.lower() not in source_extensions:
                continue

            file_text = file_path.read_text(encoding="utf-8", errors="ignore")
            if MAIN_FUNCTION_RE.search(file_text):
                main_source_paths.add(file_path.resolve())

    return main_source_paths
