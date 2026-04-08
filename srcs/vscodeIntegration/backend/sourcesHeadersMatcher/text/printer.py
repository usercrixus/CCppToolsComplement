from __future__ import annotations

from pathlib import Path

def _group_label(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix in {".h", ".hpp"}:
        return "Headers"
    return "Sources"


def _format_content_preview(file_text: str) -> str:
    lines = file_text.splitlines()
    if not lines:
        return "    <empty>"
    return "\n".join(f"    {line}" for line in lines)


def format_stringified_headers(stringified_headers: list[dict[str, str]]) -> str:
    if not stringified_headers:
        return "No files to render."

    grouped_entries: dict[str, list[dict[str, str]]] = {"Headers": [], "Sources": []}
    for entry in stringified_headers:
        grouped_entries[_group_label(entry["path"])].append(entry)

    lines = []
    for group_name in ("Headers", "Sources"):
        entries = grouped_entries[group_name]
        if not entries:
            continue

        lines.append(f"{group_name} ({len(entries)})")
        lines.append("")

        for entry in entries:
            lines.append(str(entry["path"]))
            lines.append(_format_content_preview(entry["string"]))
            lines.append("")

    return "\n".join(lines).rstrip()
