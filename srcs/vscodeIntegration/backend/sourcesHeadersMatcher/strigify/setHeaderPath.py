from __future__ import annotations

from pathlib import Path

from Classes.Symbol.Symbol import Symbol
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS


def header_path_from_source(source_path: str) -> str:
    source = Path(source_path)
    suffix = source.suffix.lower()
    if suffix in HEADER_EXTENSIONS:
        return str(source)
    header_suffix = HEADER_EXTENSIONS[SOURCE_EXTENSIONS.index(suffix)]
    return str(source.with_suffix(header_suffix))


def best_recurence_path(entry: Symbol) -> str | None:
    return entry.best_recurence_path()


def set_entry_header_paths(symbols: dict[str, Symbol]) -> None:
    for symbol_name, entry in list(symbols.items()):
        entry.header_path = entry.resolve_header_path()
        if entry.header_path is None:
            del symbols[symbol_name]
