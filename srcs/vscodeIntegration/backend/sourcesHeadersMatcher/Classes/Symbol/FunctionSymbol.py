from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.Symbol.Symbol import SYMBOL_TYPES, Symbol
from regexTools.getImplementation import get_c_function_imp
from regexTools.getProto import get_c_function_proto, get_cpp_function_proto


@dataclass(slots=True)
class FunctionSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"([A-Za-z_]\w*)\s*\(")
    REQUIRES_CALL_SYNTAX: ClassVar[bool] = True

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))

    @classmethod
    def implementation_statements_from_text(cls, file_text: str) -> list[str]:
        return get_c_function_imp(file_text)

    def resolve_header_path(self) -> str | None:
        return self.header_path_from_source(self.source)


SYMBOL_TYPES.append(FunctionSymbol)
