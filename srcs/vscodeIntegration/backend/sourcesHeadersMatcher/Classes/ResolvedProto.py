from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Collection

from regexTools.getProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)
from utils import is_excluded, normalize_excluded_paths, read_file


@dataclass(slots=True)
class ResolvedProto:
    FUNCTION_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"([A-Za-z_]\w*)\s*\(")
    MACRO_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"#\s*define\s+([A-Za-z_]\w*)")
    CLASS_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\bclass\s+([A-Za-z_]\w*)")
    STRUCT_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\bstruct\s+([A-Za-z_]\w*)")
    TYPEDEF_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\btypedef\b[\s\S]*?\b([A-Za-z_]\w*)\s*;")
    USING_NAME_RE: ClassVar[re.Pattern[str]] = re.compile(r"\busing\s+([A-Za-z_]\w*)\s*=")

    classes: set[str] = field(default_factory=set)
    functions: set[str] = field(default_factory=set)
    macros: set[str] = field(default_factory=set)
    structs: set[str] = field(default_factory=set)
    typedefs: set[str] = field(default_factory=set)

    @staticmethod
    def iter_proto_groups(
        proto_groups: "ResolvedProto",
    ) -> dict[str, tuple[Collection[str], re.Pattern[str], re.Pattern[str] | None]]:
        return {
            "class": (proto_groups.classes, ResolvedProto.CLASS_NAME_RE, None),
            "function": (proto_groups.functions, ResolvedProto.FUNCTION_NAME_RE, None),
            "macro": (proto_groups.macros, ResolvedProto.MACRO_NAME_RE, None),
            "struct": (proto_groups.structs, ResolvedProto.STRUCT_NAME_RE, None),
            "typedef": (proto_groups.typedefs, ResolvedProto.TYPEDEF_NAME_RE, ResolvedProto.USING_NAME_RE),
        }

    def _add_unique_set_value(self, values: set[str], value: str) -> None:
        if value and value not in values:
            values.add(value)

    def add_unique(self, other: "ResolvedProto") -> None:
        current_groups = {
            proto_type: protos
            for proto_type, (protos, _, _) in ResolvedProto.iter_proto_groups(self).items()
        }
        for proto_type, (protos, _, _) in ResolvedProto.iter_proto_groups(other).items():
            current_group = current_groups[proto_type]
            for proto in protos:
                self._add_unique_set_value(current_group, proto)


def collect_from_text(file_text: str) -> ResolvedProto:
    struct_proto = get_struct_proto(file_text)
    class_proto = [proto for proto in get_cpp_class_proto(file_text) if proto not in struct_proto]
    function_proto = list(dict.fromkeys(get_c_function_proto(file_text) + get_cpp_function_proto(file_text)))
    macro_proto = get_macro_proto(file_text)
    typedef_proto = get_typedef_proto(file_text)
    return ResolvedProto(
        classes=class_proto,
        functions=function_proto,
        macros=macro_proto,
        structs=struct_proto,
        typedefs=typedef_proto,
    )


def getResolvedProtoFromTexts(texts_by_path: dict[str, str]) -> ResolvedProto:
    grouped_proto = ResolvedProto()
    for file_text in texts_by_path.values():
        file_grouped_proto = collect_from_text(file_text)
        grouped_proto.add_unique(file_grouped_proto)
    return grouped_proto


def getResolvedProto(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> ResolvedProto:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath or [])
    grouped_proto = ResolvedProto()
    for file_path in start_path.rglob("*"):
        if file_path.is_file() and not is_excluded(file_path, excluded_paths) and extensions and file_path.suffix.lower() in extensions:
            file_text = read_file(file_path)
            file_grouped_proto = collect_from_text(file_text)
            grouped_proto.add_unique(file_grouped_proto)
    return grouped_proto
