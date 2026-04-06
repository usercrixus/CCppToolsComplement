from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

from Classes.ProtoMatch import ProtoMatch


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

    def append_proto_entry(self, entry: ProtoMatch) -> None:
        if entry.proto_type == "function":
            self.append_value(self.function_implementations, entry.implementation)

    def _existing_include_lines(self, file_text: str) -> set[str]:
        return {line.strip() for line in file_text.splitlines() if line.strip().startswith("#include ")}

    def _string_with_inserted_include(self, file_text: str, include_line: str) -> str:
        if include_line in self._existing_include_lines(file_text):
            return file_text

        lines = file_text.splitlines()
        insert_index = 0
        while insert_index < len(lines) and lines[insert_index].strip().startswith("#include "):
            insert_index += 1

        updated_lines = lines[:insert_index] + [include_line] + lines[insert_index:]
        return "\n".join(updated_lines) + "\n"

    def toString(self) -> str:
        source_file = Path(self.path)
        source_text = source_file.read_text(encoding="utf-8", errors="ignore")

        for header_path in sorted(self.includes):
            include_path = os.path.relpath(
                Path(header_path).resolve(),
                source_file.resolve().parent,
            )
            include_line = f'#include "{Path(include_path).as_posix()}"'
            source_text = self._string_with_inserted_include(source_text, include_line)

        for implementation in self.function_implementations:
            if implementation not in source_text:
                if source_text and not source_text.endswith("\n"):
                    source_text += "\n"
                source_text += f"\n{implementation}\n"

        return source_text
