from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path


@dataclass(slots=True)
class Header:
    path: str
    includes: set[str] = field(default_factory=set)
    macros: list[str] = field(default_factory=list)
    struct_declarations: list[str] = field(default_factory=list)
    typedef_declarations: list[str] = field(default_factory=list)
    structs: list[str] = field(default_factory=list)
    typedefs: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)

    def declarations(self) -> list[str]:
        return (
            self.macros
            + self.struct_declarations
            + self.typedef_declarations
            + self.structs
            + self.typedefs
            + self.classes
            + self.functions
        )

    def toString(self) -> str:
        include_lines = [
            f'#include "{Path(os.path.relpath(include_path, Path(self.path).resolve().parent)).as_posix()}"'
            for include_path in sorted(self.includes)
        ]
        sections = [
            "\n".join(section)
            for section in (
                self.macros,
                self.struct_declarations,
                self.typedef_declarations,
                self.structs,
                self.typedefs,
                self.classes,
                self.functions,
            )
            if section
        ]
        content_sections = []
        if include_lines:
            content_sections.append("\n".join(include_lines))
        if sections:
            content_sections.append("\n\n".join(sections))
        body = "\n\n".join(content_sections)
        if body:
            body = f"{body}\n"
        return f"#pragma once\n\n{body}"
