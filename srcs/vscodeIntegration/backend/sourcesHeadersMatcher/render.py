from pathlib import Path

from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)


def _append_unique(target_list, seen_values, value):
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _header_path_from_source(source_path):
    return str(Path(source_path).with_suffix(".h"))


def _entry_recurence_score(entry):
    return sum(recurence.get("times", 0) for recurence in entry.get("recurence", []))


def _proto_type(proto):
    if get_macro_proto(proto):
        return "macro"
    if get_struct_proto(proto):
        return "struct"
    if get_cpp_class_proto(proto):
        return "class"
    if get_typedef_proto(proto):
        return "typedef"
    if get_c_function_proto(proto):
        return "function"
    return None


def _target_headers_for_proto(proto, entries):
    proto_type = _proto_type(proto)
    if proto_type == "function":
        return [_header_path_from_source(entry["source"]) for entry in entries]

    if proto_type in {"macro", "struct", "typedef", "class"}:
        best_entry = max(entries, key=_entry_recurence_score)
        return [_header_path_from_source(best_entry["source"])]

    return []


def _build_header_map(generated_headers):
    header_map = {}
    seen_header_values = {}

    for proto, entries in generated_headers.items():
        for header_path in _target_headers_for_proto(proto, entries):
            header_map.setdefault(header_path, [])
            seen_header_values.setdefault(header_path, set())
            _append_unique(header_map[header_path], seen_header_values[header_path], proto)

    return header_map


def _render_header_content(header_path, protos):
    body = "\n".join(protos)
    if body:
        body = f"{body}\n"

    return f"#pragma once\n\n{body}"


def renderHeaders(generatedHeaders):
    header_map = _build_header_map(generatedHeaders)

    for header_path, protos in header_map.items():
        header_file = Path(header_path)
        header_file.parent.mkdir(parents=True, exist_ok=True)
        header_file.write_text(_render_header_content(header_path, protos), encoding="utf-8")

    return header_map
