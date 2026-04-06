from __future__ import annotations

from pathlib import Path

from Classes.ProtoMatch import ProtoMatch
from Classes.TypeAliases import Symbols
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS


def header_path_from_source(source_path: str) -> str:
    source = Path(source_path)
    suffix = source.suffix.lower()
    if suffix in HEADER_EXTENSIONS:
        return str(source)
    header_suffix = HEADER_EXTENSIONS[SOURCE_EXTENSIONS.index(suffix)]
    return str(source.with_suffix(header_suffix))


def best_recurence_path(entry: ProtoMatch) -> str | None:
    best_score = 0
    best_path: str | None = None
    for key, recurence in entry.recurence.items():
        if recurence >= best_score:
            best_score = recurence
            best_path = key
    return best_path


def set_entry_header_paths(symbols: Symbols) -> None:
    for symbol_name, entry in list(symbols.items()):
        if entry.proto_type == "function":
            entry.header_path = header_path_from_source(entry.source)
        else:
            best_path = best_recurence_path(entry)
            if best_path is None:
                del symbols[symbol_name]
            else:
                entry.header_path = header_path_from_source(best_path)
