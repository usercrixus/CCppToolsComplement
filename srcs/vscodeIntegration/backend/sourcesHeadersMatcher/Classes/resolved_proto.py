from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar, Iterable


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
    ) -> Iterable[tuple[str, set[str], re.Pattern[str], re.Pattern[str] | None]]:
        return (
            ("class", proto_groups.classes, ResolvedProto.CLASS_NAME_RE, None),
            ("function", proto_groups.functions, ResolvedProto.FUNCTION_NAME_RE, None),
            ("macro", proto_groups.macros, ResolvedProto.MACRO_NAME_RE, None),
            ("struct", proto_groups.structs, ResolvedProto.STRUCT_NAME_RE, None),
            ("typedef", proto_groups.typedefs, ResolvedProto.TYPEDEF_NAME_RE, ResolvedProto.USING_NAME_RE),
        )

    def _add_unique_set_value(self, values: set[str], value: str) -> None:
        if value and value not in values:
            values.add(value)

    def add_unique(self, other: "ResolvedProto") -> None:
        for proto in other.classes:
            self._add_unique_set_value(self.classes, proto)
        for proto in other.functions:
            self._add_unique_set_value(self.functions, proto)
        for proto in other.macros:
            self._add_unique_set_value(self.macros, proto)
        for proto in other.structs:
            self._add_unique_set_value(self.structs, proto)
        for proto in other.typedefs:
            self._add_unique_set_value(self.typedefs, proto)
