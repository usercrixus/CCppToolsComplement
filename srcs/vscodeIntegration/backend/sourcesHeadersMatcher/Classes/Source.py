from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.Symbol import Symbol


@dataclass(slots=True)
class Source:
    path: str
    includes: set[str] = field(default_factory=set)
    function_implementations: list[str] = field(default_factory=list)

    def append_include(self, include_path: str) -> None:
        if include_path:
            self.includes.add(str(Path(include_path).resolve()))

    def append_value(self, target_list: list[str], value: str) -> None:
        if value:
            target_list.append(value)

    def append_proto_entry(self, entry: Symbol) -> None:
        if isinstance(entry, FunctionSymbol):
            self.append_value(self.function_implementations, entry.implementation)

    def toString(self) -> str:
        include_lines = [
            f'#include "{Path(os.path.relpath(include_path, Path(self.path).resolve().parent)).as_posix()}"'
            for include_path in sorted(self.includes)
        ]
        content_sections = []
        if include_lines:
            content_sections.append("\n".join(include_lines))
        if self.function_implementations:
            content_sections.append("\n\n".join(self.function_implementations))
        body = "\n\n".join(content_sections)
        if body:
            body = f"{body}\n"
        return body
