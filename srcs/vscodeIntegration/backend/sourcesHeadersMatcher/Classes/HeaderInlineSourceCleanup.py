from __future__ import annotations

import re
from pathlib import Path

from Classes.HeaderTextsByPath import HeaderTextsByPath
from Classes.SourceTextsByPath import SourceTextsByPath
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
from regexTools.getImplementation import FUNCTION_IMP_START_RE


def _is_function_implementation_start(stripped_line: str) -> bool:
    if stripped_line.endswith(";"):
        return False
    if FUNCTION_IMP_START_RE.match(stripped_line):
        return True
    if "{" not in stripped_line:
        return False
    signature_prefix = stripped_line.split("{", 1)[0].rstrip()
    return bool(FUNCTION_IMP_START_RE.match(signature_prefix))


def _extract_function_implementation_ranges(text: str) -> list[tuple[int, int, str]]:
    lines = text.splitlines(keepends=True)
    line_offsets: list[int] = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line)

    implementation_ranges: list[tuple[int, int, str]] = []
    line_index = 0

    while line_index < len(lines):
        raw_line = lines[line_index]
        stripped_line = raw_line.strip()
        if not _is_function_implementation_start(stripped_line):
            line_index += 1
            continue

        start_index = line_index
        end_index = line_index
        brace_depth = raw_line.count("{") - raw_line.count("}")
        has_opening_brace = "{" in raw_line

        while not has_opening_brace:
            end_index += 1
            if end_index >= len(lines):
                break
            has_opening_brace = "{" in lines[end_index]
            brace_depth += lines[end_index].count("{") - lines[end_index].count("}")

        while brace_depth > 0:
            end_index += 1
            if end_index >= len(lines):
                break
            brace_depth += lines[end_index].count("{") - lines[end_index].count("}")

        if end_index >= len(lines):
            break

        start_offset = line_offsets[start_index]
        end_offset = line_offsets[end_index] + len(lines[end_index])
        implementation_text = text[start_offset:end_offset].strip()
        if implementation_text:
            implementation_ranges.append((start_offset, end_offset, implementation_text))

        line_index = end_index + 1

    return implementation_ranges


def _remove_text_ranges(text: str, ranges: list[tuple[int, int, str]]) -> str:
    if not ranges:
        return text

    chunks: list[str] = []
    cursor = 0
    for start_offset, end_offset, _ in ranges:
        chunks.append(text[cursor:start_offset])
        cursor = end_offset
    chunks.append(text[cursor:])

    cleaned_text = "".join(chunks)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    if not cleaned_text:
        return ""
    return f"{cleaned_text}\n"


def _build_fake_source_path(header_path: str) -> str:
    path = Path(header_path)
    suffix_map = dict(zip(HEADER_EXTENSIONS, SOURCE_EXTENSIONS))
    fake_source_suffix = suffix_map.get(path.suffix.lower(), ".c")
    return str(path.with_name(f"{path.stem}__header_impl{fake_source_suffix}"))


def _append_source_text(source_texts_by_path: SourceTextsByPath, source_path: str, text: str) -> None:
    current_text = source_texts_by_path.get(source_path, "").strip()
    if not current_text:
        source_texts_by_path[source_path] = f"{text}\n"
        return
    source_texts_by_path[source_path] = f"{current_text}\n\n{text}\n"


def move_header_implementations_to_sources(
    source_texts_by_path: SourceTextsByPath,
    header_texts_by_path: HeaderTextsByPath,
) -> tuple[SourceTextsByPath, HeaderTextsByPath]:
    cleaned_source_texts_by_path = dict(source_texts_by_path)
    cleaned_header_texts_by_path: HeaderTextsByPath = {}

    for header_path, header_text in header_texts_by_path.items():
        implementation_ranges = _extract_function_implementation_ranges(header_text)
        cleaned_header_texts_by_path[header_path] = _remove_text_ranges(header_text, implementation_ranges)

        if not implementation_ranges:
            continue

        fake_source_path = _build_fake_source_path(header_path)
        extracted_implementations = "\n\n".join(
            implementation_text
            for _, _, implementation_text in implementation_ranges
        )
        _append_source_text(cleaned_source_texts_by_path, fake_source_path, extracted_implementations)

    return cleaned_source_texts_by_path, cleaned_header_texts_by_path
