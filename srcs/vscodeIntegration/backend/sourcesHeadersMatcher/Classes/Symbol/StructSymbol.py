from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.ExtractedFileStatements import ExtractedFileStatements
from Classes.Symbol.Symbol import Symbol
from regexTools.getProto import get_struct_proto


@dataclass(slots=True)
class StructSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\bstruct\s+([A-Za-z_]\w*)")

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return get_struct_proto(file_text)

    @classmethod
    def find_matching_implementation(
        cls,
        declaration: str,
        extracted_file_statements: ExtractedFileStatements,
    ) -> str | None:
        declaration_name = cls.extract_symbol_name(declaration)
        if declaration_name is None:
            return None

        for struct_statement in extracted_file_statements.structs:
            if cls.extract_symbol_name(struct_statement) == declaration_name:
                return struct_statement
        return None
