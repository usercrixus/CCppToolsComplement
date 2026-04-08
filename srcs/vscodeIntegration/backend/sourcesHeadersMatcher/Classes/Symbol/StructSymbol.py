from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.Symbol.Symbol import SYMBOL_TYPES, Symbol
from regexTools.getImplementation import get_struct_imp
from regexTools.getProto import get_struct_proto


@dataclass(slots=True)
class StructSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\bstruct\s+([A-Za-z_]\w*)")

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return get_struct_proto(file_text)

    @classmethod
    def implementation_statements_from_text(cls, file_text: str) -> list[str]:
        return list(dict.fromkeys(get_struct_proto(file_text) + get_struct_imp(file_text)))


SYMBOL_TYPES.append(StructSymbol)
