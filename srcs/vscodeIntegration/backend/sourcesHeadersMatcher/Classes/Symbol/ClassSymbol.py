from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.Symbol.Symbol import SYMBOL_TYPES, Symbol
from regexTools.getImplementation import get_cpp_class_imp
from regexTools.getProto import get_cpp_class_proto, get_struct_proto


@dataclass(slots=True)
class ClassSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\bclass\s+([A-Za-z_]\w*)")

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        struct_declarations = set(get_struct_proto(file_text))
        return [declaration for declaration in get_cpp_class_proto(file_text) if declaration not in struct_declarations]

    @classmethod
    def implementation_statements_from_text(cls, file_text: str) -> list[str]:
        return get_cpp_class_imp(file_text)


SYMBOL_TYPES.append(ClassSymbol)
