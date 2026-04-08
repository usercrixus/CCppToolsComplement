from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from Classes.ExtractedFileStatements import ExtractedFileStatements
from Classes.Recurrence import Recurrence
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
from regexTools.getSymbol import extract_name


@dataclass(slots=True)
class Symbol:
    declaration: str
    implementation: str
    source: str
    recurence: Recurrence
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
        extracted_file_statements: ExtractedFileStatements,
    ) -> str | None:
        raise NotImplementedError

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
