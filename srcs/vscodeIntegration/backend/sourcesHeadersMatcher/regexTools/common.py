from __future__ import annotations

import re


FUNCTION_NAME_RE = r"[A-Za-z_]\w*(?:::\w+)*"
FUNCTION_DECLARATION_NAME_RE = re.compile(rf"({FUNCTION_NAME_RE})\s*\(")
FUNCTION_IMP_RE = re.compile(
    rf"^\s*(?:extern\s+)?[\w:\<\>\~\*&,\s]+?{FUNCTION_NAME_RE}\s*\([^;{{}}]*\)\s*(?:const\s*)?\{{\s*$",
    re.MULTILINE,
)
CLASS_PROTO_RE = re.compile(
    r"^\s*(?:template\s*<[^;{}]+>\s*)?(?:class|struct)\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*;\s*$",
    re.MULTILINE,
)
CLASS_IMP_RE = re.compile(
    r"^\s*(?:template\s*<[^;{}]+>\s*)?(?:class|struct)\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*\{\s*$",
    re.MULTILINE,
)
MACRO_PROTO_RE = re.compile(r"^\s*#\s*define\s+[A-Za-z_]\w*(?:\([^)]*\))?(?:\s+.+)?$", re.MULTILINE)
STRUCT_FORWARD_DECL_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*;\s*$",
    re.MULTILINE,
)
STRUCT_BLOCK_START_RE = re.compile(
    r"^\s*struct\s+[A-Za-z_]\w*(?:\s*:[^{;]+)?\s*\{",
)
TYPEDEF_START_RE = re.compile(r"^\s*typedef\b")
USING_PROTO_RE = re.compile(r"^\s*using\s+[A-Za-z_]\w*\s*=\s*.+;\s*$", re.MULTILINE)
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*([<"][^>"]+[>"])', re.MULTILINE)
IFDEF_RE = re.compile(r"^\s*#\s*ifdef\s+([A-Za-z_]\w*)\b")
IFNDEF_RE = re.compile(r"^\s*#\s*ifndef\s+([A-Za-z_]\w*)\b")
ELSE_RE = re.compile(r"^\s*#\s*else\b")
ENDIF_RE = re.compile(r"^\s*#\s*endif\b")
ELIF_DEFINED_RE = re.compile(
    r"^\s*#\s*elif\s+(!\s*)?defined\s*(?:\(\s*([A-Za-z_]\w*)\s*\)|\s+([A-Za-z_]\w*))"
)


def extract_matches(text: str | None, pattern: re.Pattern[str]) -> list[str]:
    if text is None:
        return []

    matches = pattern.findall(text.strip())
    if not matches:
        return []

    normalized_matches = []
    for match in matches:
        if isinstance(match, tuple):
            normalized_match = "".join(match)
        else:
            normalized_match = match
        normalized_matches.append(normalized_match.strip())

    return normalized_matches


def extract_macro_names(text: str | None) -> list[str]:
    return extract_matches(text, MACRO_PROTO_RE)


def extract_multiline_statements(text: str | None, start_pattern: re.Pattern[str]) -> list[str]:
    if text is None:
        return []

    statements = []
    lines = text.splitlines()
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        if start_pattern.match(raw_line.strip()) is None:
            line_index += 1
            continue

        statement_lines = [raw_line.rstrip()]
        brace_depth = raw_line.count("{") - raw_line.count("}")

        while True:
            stripped_line = statement_lines[-1].strip()
            if brace_depth <= 0 and stripped_line.endswith(";"):
                break

            line_index += 1
            if line_index >= len(lines):
                break

            next_line = lines[line_index]
            statement_lines.append(next_line.rstrip())
            brace_depth += next_line.count("{") - next_line.count("}")

        statement = "\n".join(statement_lines).strip()
        if statement:
            statements.append(statement)

        line_index += 1

    return statements


def extract_function_statements(text: str | None, trailer: str) -> list[str]:
    if text is None:
        return []

    matches = []
    for raw_line in text.splitlines():
        stripped_line = raw_line.strip()
        if not stripped_line or not stripped_line.endswith(trailer):
            continue
        if stripped_line.startswith("#"):
            continue
        if "(" not in stripped_line or ")" not in stripped_line:
            continue
        if re.match(r"^(return|if|for|while|switch)\b", stripped_line):
            continue
        if "=" in stripped_line.partition("(")[0]:
            continue

        name_match = FUNCTION_DECLARATION_NAME_RE.search(stripped_line)
        if name_match is None:
            continue

        prefix = stripped_line[:name_match.start()].strip()
        if prefix.startswith("extern "):
            prefix = prefix[len("extern "):].strip()
        if not prefix:
            continue

        matches.append(stripped_line)

    return matches
