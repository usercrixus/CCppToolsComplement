from __future__ import annotations
from pathlib import Path
from Classes.resolved_proto import ResolvedProto
from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)
from utils import _is_excluded, _normalize_excluded_paths, _read_file


def _collect_from_text(file_text: str) -> ResolvedProto:
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


def resolveProto(startPath: str, extensions: set[str], excludedFolderPath: list[str] | None = None) -> ResolvedProto:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath or [])
    grouped_proto = ResolvedProto()
    for file_path in start_path.rglob("*"):
        if file_path.is_file() and not _is_excluded(file_path, excluded_paths) and extensions and file_path.suffix.lower() in extensions:
            file_text = _read_file(file_path)
            file_grouped_proto = _collect_from_text(file_text)
            grouped_proto.add_unique(file_grouped_proto)
    return grouped_proto
