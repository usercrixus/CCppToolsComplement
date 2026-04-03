from __future__ import annotations
from dataclasses import dataclass
from Classes.recurrence import Recurrence

@dataclass(slots=True)
class ProtoMatch:
    implementation: str
    source: str
    recurence: list[Recurrence]
    header_path: str | None = None
