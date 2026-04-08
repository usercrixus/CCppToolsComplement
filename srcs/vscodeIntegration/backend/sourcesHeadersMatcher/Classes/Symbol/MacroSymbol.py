from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar

from Classes.Symbol.Symbol import SYMBOL_TYPES, Symbol
from regexTools.getProto import get_macro_proto


@dataclass(slots=True)
class MacroSymbol(Symbol):
    NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"#\s*define\s+([A-Za-z_]\w*)")
    REQUIRES_CALL_SYNTAX: ClassVar[bool] = True

    @classmethod
    def declarations_from_text(cls, file_text: str) -> list[str]:
        return get_macro_proto(file_text)

    @classmethod
    def find_matching_implementation(
        cls,
        declaration: str,
        file_text: str,
    ) -> str | None:
        return declaration if declaration in get_macro_proto(file_text) else None


SYMBOL_TYPES.append(MacroSymbol)
