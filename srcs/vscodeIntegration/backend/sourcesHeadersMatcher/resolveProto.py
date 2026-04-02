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


def _extract_grouped_proto(proto_text):
    struct_matches = get_struct_proto(proto_text)
    if struct_matches:
        return (("struct", struct_matches),)

    class_matches = get_cpp_class_proto(proto_text)
    if class_matches:
        return (("class", class_matches),)

    function_matches = get_c_function_proto(proto_text) + get_cpp_function_proto(proto_text)
    if function_matches:
        return (("function", function_matches),)

    macro_matches = get_macro_proto(proto_text)
    if macro_matches:
        return (("macro", macro_matches),)

    typedef_matches = get_typedef_proto(proto_text)
    if typedef_matches:
        return (("typedef", typedef_matches),)

    return ()


def resolveProto(protoMap):
    grouped_proto = {proto_type: [] for proto_type in PROTO_GROUP_ORDER}
    seen_group_values = {proto_type: set() for proto_type in PROTO_GROUP_ORDER}

    for entries in protoMap.values():
        for entry in entries:
            proto_text = _get_entry_text(entry).strip()
            for proto_type, matches in _extract_grouped_proto(proto_text):
                for match in matches:
                    _append_unique(grouped_proto[proto_type], seen_group_values[proto_type], match)

    return [grouped_proto[proto_type] for proto_type in PROTO_GROUP_ORDER]
