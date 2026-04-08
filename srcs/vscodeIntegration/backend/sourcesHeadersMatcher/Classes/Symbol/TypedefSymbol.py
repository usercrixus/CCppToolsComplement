from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.ExtractedFileStatements import ExtractedFileStatements
from Classes.Symbol.Symbol import Symbol
from regexTools.getProto import get_typedef_proto
from regexTools.getSymbol import extract_name, extract_typedef_name


@dataclass(slots=True)
class TypedefSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\btypedef\b[\s\S]*?\b([A-Za-z_]\w*)\s*;")
    USING_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\busing\s+([A-Za-z_]\w*)\s*=")

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return get_typedef_proto(file_text)

    @classmethod
    def extract_symbol_name(cls, statement: str) -> str | None:
        using_name = extract_name(statement, cls.USING_NAME_RE)
        if using_name is not None:
            return using_name
        return extract_typedef_name(statement)

    @classmethod
    def find_matching_implementation(
        cls,
        declaration: str,
        extracted_file_statements: ExtractedFileStatements,
    ) -> str | None:
        declaration_name = cls.extract_symbol_name(declaration)
        if declaration_name is None:
            return None

        for typedef_statement in extracted_file_statements.typedefs:
            if cls.extract_symbol_name(typedef_statement) == declaration_name:
                return typedef_statement
        return None
