from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class ExtractedFileStatements:
    classes: list[str]
    function_implementations: list[str]
    macros: list[str]
    structs: list[str]
    typedefs: list[str]
