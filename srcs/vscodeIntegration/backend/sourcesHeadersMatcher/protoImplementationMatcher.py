from getSourceProto import (
    get_c_function_imp,
    get_macro_proto,
    get_struct_imp,
    get_struct_proto,
    get_typedef_proto,
)
import re


PROTO_TYPE_INDEX = {
    "class": 0,
    "function": 1,
    "macro": 2,
    "struct": 3,
    "typedef": 4,
}

FUNCTION_NAME_RE = re.compile(r"([A-Za-z_]\w*)\s*\(")
MACRO_NAME_RE = re.compile(r"#\s*define\s+([A-Za-z_]\w*)")
STRUCT_NAME_RE = re.compile(r"\bstruct\s+([A-Za-z_]\w*)")
TYPEDEF_NAME_RE = re.compile(r"\btypedef\b.*?\b([A-Za-z_]\w*)\s*;")
USING_NAME_RE = re.compile(r"\busing\s+([A-Za-z_]\w*)\s*=")


def _extract_name(statement, pattern):
    match = pattern.search(statement)
    if match is None:
        return None
    return match.group(1)


def _extract_typedef_name(statement):
    using_name = _extract_name(statement, USING_NAME_RE)
    if using_name is not None:
        return using_name
    return _extract_name(statement, TYPEDEF_NAME_RE)


def _count_recurence(file_text, symbol_name):
    if not symbol_name:
        return 0
    return max(len(re.findall(rf"\b{re.escape(symbol_name)}\b", file_text)) - 1, 0)


def _build_recurence(file_path, file_text, symbol_name):
    return [
        {
            "source": str(file_path),
            "times": _count_recurence(file_text, symbol_name),
        }
    ]


def _find_matching_function_imp(proto, function_imps):
    proto_name = _extract_name(proto, FUNCTION_NAME_RE)
    if proto_name is None:
        return None

    for function_imp in function_imps:
        if _extract_name(function_imp, FUNCTION_NAME_RE) == proto_name:
            return function_imp
    return None


def _find_matching_struct(proto, struct_statements):
    proto_name = _extract_name(proto, STRUCT_NAME_RE)
    if proto_name is None:
        return None

    for struct_statement in struct_statements:
        if _extract_name(struct_statement, STRUCT_NAME_RE) == proto_name:
            return struct_statement
    return None


def _find_matching_typedef(proto, typedef_statements):
    proto_name = _extract_typedef_name(proto)
    if proto_name is None:
        return None

    for typedef_statement in typedef_statements:
        if _extract_typedef_name(typedef_statement) == proto_name:
            return typedef_statement
    return None


def _match_proto(proto_type, proto, file_text, extracted_file_statements):
    if proto_type == "function":
        return _find_matching_function_imp(proto, extracted_file_statements["function_imp"])
    if proto_type == "macro":
        return proto if proto in extracted_file_statements["macro"] else None
    if proto_type == "struct":
        return _find_matching_struct(proto, extracted_file_statements["struct"])
    if proto_type == "typedef":
        return _find_matching_typedef(proto, extracted_file_statements["typedef"])
    return None


def extract_file_statements(file_text):
    return {
        "function_imp": get_c_function_imp(file_text),
        "macro": get_macro_proto(file_text),
        "struct": list(dict.fromkeys(get_struct_proto(file_text) + get_struct_imp(file_text))),
        "typedef": get_typedef_proto(file_text),
    }


def build_proto_map(file_path, proto_groups, file_text):
    extracted_file_statements = extract_file_statements(file_text)
    result_map = {}

    for proto_type, proto_index in PROTO_TYPE_INDEX.items():
        if proto_type == "class":
            continue

        for proto in proto_groups[proto_index]:
            implementation = _match_proto(proto_type, proto, file_text, extracted_file_statements)
            if implementation is None:
                continue

            if proto_type == "function":
                symbol_name = _extract_name(proto, FUNCTION_NAME_RE)
            elif proto_type == "macro":
                symbol_name = _extract_name(proto, MACRO_NAME_RE)
            elif proto_type == "struct":
                symbol_name = _extract_name(proto, STRUCT_NAME_RE)
            else:
                symbol_name = _extract_typedef_name(proto)

            entry = {
                "implementation": implementation,
                "source": str(file_path),
                "recurence": _build_recurence(file_path, file_text, symbol_name),
            }
            result_map.setdefault(proto, []).append(entry)

    return result_map
