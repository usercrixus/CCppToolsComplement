from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from Classes.RenderJob import RenderJob
from Classes.Symbol.ClassSymbol import ClassSymbol
from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.MacroSymbol import MacroSymbol
from Classes.Symbol.Symbol import Symbol
from Classes.Symbol.StructSymbol import StructSymbol
from Classes.Symbol.TypedefSymbol import TypedefSymbol
from regexTools.getSymbol import extract_struct_name, extract_typedef_name


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

    def append_value(self, target_list: list[str], value: str) -> None:
        if value:
            target_list.append(value)

    def append_struct_entry(self, entry: Symbol) -> None:
        struct_name = extract_struct_name(entry.declaration)
        if "{" in entry.declaration and struct_name is not None:
            self.append_value(self.struct_declarations, f"struct {struct_name};")
            self.append_value(self.structs, entry.implementation)
            return

        self.append_value(self.struct_declarations, entry.declaration)

    def append_typedef_entry(self, entry: Symbol) -> None:
        typedef_name = extract_typedef_name(entry.declaration)
        struct_name = extract_struct_name(entry.declaration)
        if "{" in entry.declaration and typedef_name is not None and struct_name is not None:
            self.append_value(
                self.typedef_declarations,
                f"typedef struct {struct_name} {typedef_name};",
            )
            self.append_value(self.typedefs, entry.implementation)
            return

        self.append_value(self.typedef_declarations, entry.declaration)

    def append_proto_entry(self, entry: Symbol) -> None:
        if isinstance(entry, MacroSymbol):
            self.append_value(self.macros, entry.declaration)
        elif isinstance(entry, StructSymbol):
            self.append_struct_entry(entry)
        elif isinstance(entry, TypedefSymbol):
            self.append_typedef_entry(entry)
        elif isinstance(entry, ClassSymbol):
            self.append_value(self.classes, entry.declaration)
        elif isinstance(entry, FunctionSymbol):
            self.append_value(self.functions, entry.declaration)

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

    @staticmethod
    def create_include_set_render_job(path: str, include_set: set[str]) -> RenderJob:
        output_path = Path(path).resolve()
        include_lines = []
        for include in sorted(include_set):
            if include.startswith("<") and include.endswith(">"):
                include_lines.append(f"#include {include}")
                continue
            relative_include = Path(os.path.relpath(include, output_path.parent)).as_posix()
            include_lines.append(f'#include "{relative_include}"')
        body = "\n".join(include_lines)
        if body:
            body = f"{body}\n"
        return RenderJob(path=path, string=f"#pragma once\n\n{body}")

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
