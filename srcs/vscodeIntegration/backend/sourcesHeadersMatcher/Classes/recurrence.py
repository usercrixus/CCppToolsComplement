from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class Recurrence:
    source: str
    times: int
