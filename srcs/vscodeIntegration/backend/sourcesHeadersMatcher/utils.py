from __future__ import annotations
from pathlib import Path


def _normalize_excluded_paths(excluded_folder_paths: list[str]) -> set[Path]:
    return {
        Path(folder_path).expanduser().resolve()
        for folder_path in excluded_folder_paths
    }


def _is_excluded(path: Path, excluded_paths: set[Path]) -> bool:
    return any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded_paths)


def _read_file(file_path: Path) -> str:
    return Path(file_path).read_text(encoding="utf-8", errors="ignore")


def _write_file(file_path: Path, file_text: str) -> None:
    Path(file_path).write_text(file_text, encoding="utf-8")
