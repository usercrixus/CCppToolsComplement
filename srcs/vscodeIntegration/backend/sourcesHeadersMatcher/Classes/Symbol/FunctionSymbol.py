from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.ExtractedFileStatements import ExtractedFileStatements
from Classes.Symbol.Symbol import Symbol
from regexTools.getProto import get_c_function_proto, get_cpp_function_proto


@dataclass(slots=True)
class FunctionSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"([A-Za-z_]\w*)\s*\(")
    REQUIRES_CALL_SYNTAX: ClassVar[bool] = True

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))

    @classmethod
    def find_matching_implementation(
        cls,
        declaration: str,
        extracted_file_statements: ExtractedFileStatements,
    ) -> str | None:
        declaration_name = cls.extract_symbol_name(declaration)
        if declaration_name is None:
            return None

        for function_imp in extracted_file_statements.function_implementations:
            if cls.extract_symbol_name(function_imp) == declaration_name:
                return function_imp
        return None

    def resolve_header_path(self) -> str | None:
        return self.header_path_from_source(self.source)
