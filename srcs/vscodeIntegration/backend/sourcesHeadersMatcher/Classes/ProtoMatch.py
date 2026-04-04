from __future__ import annotations
from dataclasses import dataclass
from Classes.Recurrence import Recurrence

@dataclass(slots=True)
class ProtoMatch:
    declaration: str
    symbol_name: str
    proto_type: str
    implementation: str
    source: str
    recurence: Recurrence
    header_path: str | None = None
