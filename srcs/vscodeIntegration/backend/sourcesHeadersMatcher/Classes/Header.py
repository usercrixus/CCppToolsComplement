from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re

from Classes.HeaderTextsByPath import HeaderTextsByPath
from Classes.RenderJob import RenderJob
from Classes.SourceTextsByPath import SourceTextsByPath
from Classes.Symbol.ClassSymbol import ClassSymbol
from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.MacroSymbol import MacroSymbol
from Classes.Symbol.Symbol import Symbol
from Classes.Symbol.StructSymbol import StructSymbol
from Classes.Symbol.TypedefSymbol import TypedefSymbol
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
from regexTools.getImplementation import FUNCTION_IMP_START_RE
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


def _is_function_implementation_start(stripped_line: str) -> bool:
    if stripped_line.endswith(";"):
        return False
    if FUNCTION_IMP_START_RE.match(stripped_line):
        return True
    if "{" not in stripped_line:
        return False
    signature_prefix = stripped_line.split("{", 1)[0].rstrip()
    return bool(FUNCTION_IMP_START_RE.match(signature_prefix))


def _extract_function_implementation_ranges(text: str) -> list[tuple[int, int, str]]:
    lines = text.splitlines(keepends=True)
    line_offsets: list[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    implementation_ranges: list[tuple[int, int, str]] = []
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        stripped_line = raw_line.strip()
        if not _is_function_implementation_start(stripped_line):
            line_index += 1
            continue

        start_index = line_index
        end_index = line_index
        brace_depth = raw_line.count("{") - raw_line.count("}")
        has_opening_brace = "{" in raw_line

        while not has_opening_brace:
            end_index += 1
            if end_index >= len(lines):
                break
            has_opening_brace = "{" in lines[end_index]
            brace_depth += lines[end_index].count("{") - lines[end_index].count("}")

        while brace_depth > 0:
            end_index += 1
            if end_index >= len(lines):
                break
            brace_depth += lines[end_index].count("{") - lines[end_index].count("}")

        if end_index >= len(lines):
            break

        start_offset = line_offsets[start_index]
        end_offset = line_offsets[end_index] + len(lines[end_index])
        implementation_text = text[start_offset:end_offset].strip()
        if implementation_text:
            implementation_ranges.append((start_offset, end_offset, implementation_text))

        line_index = end_index + 1

    return implementation_ranges


def _remove_text_ranges(text: str, ranges: list[tuple[int, int, str]]) -> str:
    if not ranges:
        return text

    chunks: list[str] = []
    cursor = 0
    for start_offset, end_offset, _ in ranges:
        chunks.append(text[cursor:start_offset])
        cursor = end_offset
    chunks.append(text[cursor:])

    cleaned_text = "".join(chunks)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    if not cleaned_text:
        return ""
    return f"{cleaned_text}\n"


def _build_fake_source_path(header_path: str) -> str:
    path = Path(header_path)
    suffix_map = dict(zip(HEADER_EXTENSIONS, SOURCE_EXTENSIONS))
    fake_source_suffix = suffix_map.get(path.suffix.lower(), ".c")
    return str(path.with_name(f"{path.stem}__header_impl{fake_source_suffix}"))


def _append_source_text(source_texts_by_path: SourceTextsByPath, source_path: str, text: str) -> None:
    current_text = source_texts_by_path.get(source_path, "").strip()
    if not current_text:
        source_texts_by_path[source_path] = f"{text}\n"
        return
    source_texts_by_path[source_path] = f"{current_text}\n\n{text}\n"


def move_header_implementations_to_sources(
    source_texts_by_path: SourceTextsByPath,
    header_texts_by_path: HeaderTextsByPath,
) -> tuple[SourceTextsByPath, HeaderTextsByPath]:
    cleaned_source_texts_by_path = dict(source_texts_by_path)
    cleaned_header_texts_by_path: HeaderTextsByPath = {}

    for header_path, header_text in header_texts_by_path.items():
        implementation_ranges = _extract_function_implementation_ranges(header_text)
        cleaned_header_texts_by_path[header_path] = _remove_text_ranges(header_text, implementation_ranges)

        if not implementation_ranges:
            continue

        fake_source_path = _build_fake_source_path(header_path)
        extracted_implementations = "\n\n".join(
            implementation_text
            for _, _, implementation_text in implementation_ranges
        )
        _append_source_text(cleaned_source_texts_by_path, fake_source_path, extracted_implementations)

    return cleaned_source_texts_by_path, cleaned_header_texts_by_path
