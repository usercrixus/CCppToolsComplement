from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
from regexTools.getSymbol import extract_name

SYMBOL_TYPES: list[type[Symbol]] = []

@dataclass(slots=True)
class Symbol:
    declaration: str
    implementation: str
    source: str
    recurence: dict[str, int]
    header_path: str | None = None

    NAME_RE: ClassVar[re.Pattern[str] | None] = None
    REQUIRES_CALL_SYNTAX: ClassVar[bool] = False

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return []

    @classmethod
    def extract_symbol_name(cls, statement: str) -> str | None:
        if cls.NAME_RE is None:
            return None
        return extract_name(statement, cls.NAME_RE)

    @classmethod
    def find_matching_implementation(
        cls,
        declaration: str,
        file_text: str,
    ) -> str | None:
        declaration_name = cls.extract_symbol_name(declaration)
        if declaration_name is None:
            return None

        for statement in cls.implementation_statements_from_text(file_text):
            if cls.extract_symbol_name(statement) == declaration_name:
                return statement
        return None

    @classmethod
    def implementation_statements_from_text(cls, file_text: str) -> list[str]:
        return []

    def usage_pattern(self) -> re.Pattern[str] | None:
        symbol_name = type(self).extract_symbol_name(self.declaration)
        if not symbol_name:
            return None
        escaped_symbol_name = re.escape(symbol_name)
        if type(self).REQUIRES_CALL_SYNTAX:
            return re.compile(rf"\b{escaped_symbol_name}\b\s*(?=\()")
        return re.compile(rf"\b{escaped_symbol_name}\b")

    def resolve_header_path(self) -> str | None:
        best_path = self.best_recurence_path()
        if best_path is None:
            return None
        return self.header_path_from_source(best_path)

    @staticmethod
    def best_recurence_path_for_symbol(symbol: "Symbol") -> str | None:
        best_score = 0
        best_path: str | None = None
        for key, recurence in symbol.recurence.items():
            if recurence >= best_score:
                best_score = recurence
                best_path = key
        return best_path

    def best_recurence_path(self) -> str | None:
        return self.best_recurence_path_for_symbol(self)

    @staticmethod
    def header_path_from_source(source_path: str) -> str:
        source = Path(source_path)
        suffix = source.suffix.lower()
        if suffix in HEADER_EXTENSIONS:
            return str(source)
        header_suffix = HEADER_EXTENSIONS[SOURCE_EXTENSIONS.index(suffix)]
        return str(source.with_suffix(header_suffix))


def countProtoUsage(symbol: Symbol, source_text: str) -> int:
    usage_pattern = symbol.usage_pattern()
    if usage_pattern is None:
        return 0
    return len(usage_pattern.findall(source_text))


def setRecurence(symbols: dict[str, Symbol], source_texts_by_path: dict[str, str]) -> None:
    for source_path, source_text in source_texts_by_path.items():
        for symbol in symbols.values():
            recurence = countProtoUsage(symbol, source_text)
            if recurence > 0:
                symbol.recurence[source_path] = symbol.recurence.get(source_path, 0) + recurence


def correctIncludeSet(symbols: dict[str, Symbol], include_set: set[str]) -> set[str]:
    for symbol in symbols.values():
        if symbol.header_path is None:
            continue
        include_path = Path(symbol.header_path)
        include_set.discard(symbol.header_path)
        include_set.discard(include_path.name)
        include_set.discard(f'"{include_path.name}"')
        include_set.discard(f"<{include_path.name}>")
    return include_set


def set_entry_header_paths(symbols: dict[str, Symbol]) -> None:
    for symbol_name, entry in list(symbols.items()):
        entry.header_path = entry.resolve_header_path()
        if entry.header_path is None:
            del symbols[symbol_name]


def collect_symbol_declarations_from_texts(texts_by_path: dict[str, str]) -> dict[type[Symbol], set[str]]:
    declarations_by_type = {symbol_type: set() for symbol_type in SYMBOL_TYPES}
    for file_text in texts_by_path.values():
        for symbol_type in SYMBOL_TYPES:
            declarations_by_type[symbol_type].update(symbol_type.declarations_from_text(file_text))
    return declarations_by_type


def build_symbol_map(
    file_path: str | Path,
    declarations_by_type: dict[type[Symbol], set[str]],
    file_text: str,
) -> dict[str, Symbol]:
    file_path = Path(file_path).expanduser().resolve()
    result_map: dict[str, Symbol] = {}
    for symbol_type, declarations in declarations_by_type.items():
        for declaration in declarations:
            implementation = symbol_type.find_matching_implementation(declaration, file_text)
            if implementation is None:
                continue
            symbol_name = symbol_type.extract_symbol_name(declaration)
            if symbol_name is None:
                continue
            result_map[symbol_name] = symbol_type(
                declaration=declaration,
                implementation=implementation,
                source=str(file_path),
                recurence={},
            )
    return result_map


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
    source_texts_by_path: dict[str, str],
    merged_texts_by_path: dict[str, str],
) -> dict[str, Symbol]:
    symbols: dict[str, Symbol] = {}
    declarations_by_type = collect_symbol_declarations_from_texts(merged_texts_by_path)

    for source_path, source_text in source_texts_by_path.items():
        process_source_text(source_path, source_text, declarations_by_type, symbols)

    return symbols


def getSymbolMap(
    source_texts_by_path: dict[str, str],
    merged_texts_by_path: dict[str, str],
) -> dict[str, Symbol]:
    symbols = getSymbols(source_texts_by_path, merged_texts_by_path)
    setRecurence(symbols, source_texts_by_path)
    set_entry_header_paths(symbols)
    return symbols
