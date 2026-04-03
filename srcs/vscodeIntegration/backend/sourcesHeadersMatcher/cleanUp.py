from __future__ import annotations

from pathlib import Path

from getSourceProto import (
    get_c_function_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_forward_decl,
    get_struct_imp,
    get_typedef_proto,
)
from utils import _is_excluded, _normalize_excluded_paths, _read_file, _write_file


def _delete_file(file_path: Path) -> None:
    Path(file_path).unlink()


def _delete_empty_source_files(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if extensions and file_path.suffix.lower() not in extensions:
            continue

        file_text = _read_file(file_path)
        if file_text.strip():
            continue

        _delete_file(file_path)


def _remove_statements_from_text(file_text: str, statements: list[str]) -> str:
    updated_text = file_text
    for statement in statements:
        if not statement:
            continue

        statement_with_newline = f"{statement}\n"
        if statement_with_newline in updated_text:
            updated_text = updated_text.replace(statement_with_newline, "")
        else:
            updated_text = updated_text.replace(statement, "")

    return updated_text


def remove_function_proto_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if extensions and file_path.suffix.lower() not in extensions:
            continue

        file_text = _read_file(file_path)
        function_proto = list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))
        if not function_proto:
            continue

        updated_text = _remove_statements_from_text(file_text, function_proto)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def remove_struct_declarations_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if extensions and file_path.suffix.lower() not in extensions:
            continue

        file_text = _read_file(file_path)
        struct_statements = list(
            dict.fromkeys(
                get_struct_forward_decl(file_text)
                + get_struct_imp(file_text)
            )
        )
        typedef_statements = get_typedef_proto(file_text)
        statements_to_remove = list(dict.fromkeys(struct_statements + typedef_statements))
        if not statements_to_remove:
            continue

        updated_text = _remove_statements_from_text(file_text, statements_to_remove)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def remove_macro_definitions_from_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])

    for file_path in start_path.rglob("*"):
        if not file_path.is_file():
            continue
        if _is_excluded(file_path, excluded_paths):
            continue
        if extensions and file_path.suffix.lower() not in extensions:
            continue

        file_text = _read_file(file_path)
        macro_statements = get_macro_proto(file_text)
        if not macro_statements:
            continue

        updated_text = _remove_statements_from_text(file_text, macro_statements)
        if updated_text != file_text:
            _write_file(file_path, updated_text)


def cleanup_sources(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> None:
    remove_function_proto_from_sources(startPath, extensions, excludedFolderPath)
    remove_macro_definitions_from_sources(startPath, extensions, excludedFolderPath)
    remove_struct_declarations_from_sources(startPath, extensions, excludedFolderPath)
    _delete_empty_source_files(startPath, extensions, excludedFolderPath)
