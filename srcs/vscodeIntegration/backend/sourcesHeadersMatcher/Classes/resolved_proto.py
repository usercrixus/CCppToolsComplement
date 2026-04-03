from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ResolvedProto:
    classes: set[str] = field(default_factory=set)
    functions: set[str] = field(default_factory=set)
    macros: set[str] = field(default_factory=set)
    structs: set[str] = field(default_factory=set)
    typedefs: set[str] = field(default_factory=set)

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
