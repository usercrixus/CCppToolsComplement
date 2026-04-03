from __future__ import annotations
from dataclasses import dataclass
from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders

@dataclass(slots=True)
class TraversalResult:
    proto: ResolvedProto
    generated_headers: GeneratedHeaders
