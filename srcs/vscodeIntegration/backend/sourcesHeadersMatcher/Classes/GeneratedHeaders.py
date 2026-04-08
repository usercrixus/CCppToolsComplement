from __future__ import annotations

from Classes.ResolvedProto import ResolvedProto
from Classes.SourceTextsByPath import SourceTextsByPath
from Classes.Symbols import Symbols, build_proto_map


def merge_header_map(global_header_map: Symbols, file_header_map: Symbols) -> None:
    global_header_map.update(file_header_map)


def process_source_text(
    source_path: str,
    source_text: str,
    proto: ResolvedProto,
    symbols: Symbols,
) -> None:
    file_header_map = build_proto_map(source_path, proto, source_text)
    merge_header_map(symbols, file_header_map)


def getSymbols(
    source_texts_by_path: SourceTextsByPath,
    protos: ResolvedProto,
) -> Symbols:
    symbols: Symbols = {}

    for source_path, source_text in source_texts_by_path.items():
        process_source_text(source_path, source_text, protos, symbols)

    return symbols
