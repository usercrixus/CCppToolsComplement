from __future__ import annotations

from pathlib import Path
import re

from Classes.Source.Source import Source
from Classes.Symbol.FunctionSymbol import FunctionSymbol
from Classes.Symbol.Symbol import Symbol

_CONDITIONAL_SUFFIX_RE = re.compile(r"_conditional_[^./\\]+$")


def _append_header_family_includes(source: Source, header_path: str) -> None:
    resolved_header_path = Path(header_path).resolve()
    source.append_include(str(resolved_header_path))

def _append_conditional_family_includes(
    source: Source,
    header_path: str,
    available_header_paths: set[str],
) -> None:
    resolved_header_path = Path(header_path).resolve()
    base_stem = _CONDITIONAL_SUFFIX_RE.sub("", resolved_header_path.stem)
    conditional_prefix = f"{base_stem}_conditional_"

    for candidate_header_path in sorted(available_header_paths):
        candidate_path = Path(candidate_header_path).resolve()
        if candidate_path.parent != resolved_header_path.parent:
            continue
        if candidate_path.suffix != resolved_header_path.suffix:
            continue
        if not candidate_path.stem.startswith(conditional_prefix):
            continue
        source.append_include(str(candidate_path))


def getSourceMap(symbols: dict[str, Symbol]) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    available_header_paths = {
        str(Path(entry.header_path).resolve())
        for entry in symbols.values()
        if entry.header_path
    }

    for entry in symbols.values():
        if not isinstance(entry, FunctionSymbol):
            continue

        source_path = str(Path(entry.source).resolve())
        source = sources.setdefault(source_path, Source(path=source_path))
        source.append_proto_entry(entry)

        header_path = entry.header_path
        if not header_path:
            continue

        _append_header_family_includes(source, header_path)
        _append_conditional_family_includes(source, header_path, available_header_paths)

    return sources
