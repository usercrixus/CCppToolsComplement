from getSourceProto import (
    get_c_function_proto,
    get_cpp_class_proto,
    get_cpp_function_proto,
    get_macro_proto,
    get_struct_proto,
    get_typedef_proto,
)


PROTO_GROUP_ORDER = ("class", "function", "macro", "struct", "typedef")


def _get_entry_text(entry):
    if isinstance(entry, dict):
        return entry.get("implementation", "")
    if isinstance(entry, str):
        return entry
    return ""


def _append_unique(target_list, seen_values, value):
    if not value or value in seen_values:
        return
    seen_values.add(value)
    target_list.append(value)


def _classify_proto(proto_text):
    if get_struct_proto(proto_text):
        return "struct"
    if get_cpp_class_proto(proto_text):
        return "class"
    if get_c_function_proto(proto_text) or get_cpp_function_proto(proto_text):
        return "function"
    if get_macro_proto(proto_text):
        return "macro"
    if get_typedef_proto(proto_text):
        return "typedef"
    return None


def resolveProto(protoMap):
    grouped_proto = {proto_type: [] for proto_type in PROTO_GROUP_ORDER}
    seen_group_values = {proto_type: set() for proto_type in PROTO_GROUP_ORDER}

    for entries in protoMap.values():
        for entry in entries:
            proto_text = _get_entry_text(entry).strip()
            proto_type = _classify_proto(proto_text)
            if proto_type is None:
                continue
            _append_unique(grouped_proto[proto_type], seen_group_values[proto_type], proto_text)

    return [grouped_proto[proto_type] for proto_type in PROTO_GROUP_ORDER]
