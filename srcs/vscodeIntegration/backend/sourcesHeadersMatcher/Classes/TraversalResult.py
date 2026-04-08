from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from Classes.Symbol.Symbol import Symbol
from Classes.SourceTextsByPath import SourceTextsByPath
from Classes.GeneratedHeaders import getSymbols
from strigify.setHeaderPath import set_entry_header_paths


@dataclass(slots=True)
class TraversalResult:
    symbols: dict[str, Symbol]

    def correctIncludeSet(self, include_set: set[str]) -> set[str]:
        for symbol in self.symbols.values():
            if symbol.header_path is None:
                continue
            include_path = Path(symbol.header_path)
            include_set.discard(symbol.header_path)
            include_set.discard(include_path.name)
            include_set.discard(f'"{include_path.name}"')
            include_set.discard(f"<{include_path.name}>")
        return include_set


def countProtoUsage(symbol: Symbol, source_text: str) -> int:
    usage_pattern = symbol.usage_pattern()
    if usage_pattern is None:
        return 0
    return len(usage_pattern.findall(source_text))


def setRecurence(symbols: dict[str, Symbol], source_texts_by_path: SourceTextsByPath) -> None:
    for source_path, source_text in source_texts_by_path.items():
        for symbol in symbols.values():
            recurence = countProtoUsage(symbol, source_text)
            if recurence > 0:
                symbol.recurence[source_path] = symbol.recurence.get(source_path, 0) + recurence


def getTraversalResult(
    source_texts_by_path: SourceTextsByPath,
    merged_texts_by_path: dict[str, str],
) -> TraversalResult:
    symbols = getSymbols(source_texts_by_path, merged_texts_by_path)
    setRecurence(symbols, source_texts_by_path)
    set_entry_header_paths(symbols)
    return TraversalResult(
        symbols=symbols,
    )
