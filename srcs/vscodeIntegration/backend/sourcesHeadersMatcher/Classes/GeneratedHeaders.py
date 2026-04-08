from __future__ import annotations

from Classes.Symbol.Symbol import Symbol
from Classes.Symbol.Helpers import build_symbol_map, collect_symbol_declarations_from_texts
from Classes.SourceTextsByPath import SourceTextsByPath


def merge_header_map(global_header_map: dict[str, Symbol], file_header_map: dict[str, Symbol]) -> None:
    global_header_map.update(file_header_map)


def process_source_text(
    source_path: str,
    source_text: str,
    declarations_by_type: dict[type[Symbol], set[str]],
    symbols: dict[str, Symbol],
) -> None:
    file_header_map = build_symbol_map(source_path, declarations_by_type, source_text)
    merge_header_map(symbols, file_header_map)


def getSymbols(
    source_texts_by_path: SourceTextsByPath,
    merged_texts_by_path: dict[str, str],
) -> dict[str, Symbol]:
    symbols: dict[str, Symbol] = {}
    declarations_by_type = collect_symbol_declarations_from_texts(merged_texts_by_path)

    for source_path, source_text in source_texts_by_path.items():
        process_source_text(source_path, source_text, declarations_by_type, symbols)

    return symbols
