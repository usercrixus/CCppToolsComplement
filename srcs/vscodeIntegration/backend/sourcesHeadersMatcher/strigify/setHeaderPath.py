from __future__ import annotations

from pathlib import Path

from Classes.GeneratedHeaders import GeneratedHeaders
from Classes.ProtoMatch import ProtoMatch
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS


def header_path_from_source(source_path: str) -> str:
    source = Path(source_path)
    suffix = source.suffix.lower()
    if suffix in HEADER_EXTENSIONS:
        return str(source)
    if suffix == ".c":
        return str(source.with_suffix(".h"))
    if suffix == ".cpp":
        return str(source.with_suffix(".hpp"))
    return str(source.with_suffix(".h"))


def entry_recurence_score(entry: ProtoMatch) -> int:
    return sum(entry.recurence.values())


def set_entry_header_paths(generated_headers: GeneratedHeaders) -> None:
    for entry in generated_headers.values():
        proto_type = entry.proto_type
        if proto_type == "function":
            entry.header_path = header_path_from_source(entry.source)
            continue

        entry.header_path = header_path_from_source(entry.source)
