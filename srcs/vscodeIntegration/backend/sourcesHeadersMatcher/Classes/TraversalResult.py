from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from Classes.ProtoMatch import ProtoMatch
from Classes.ResolvedProto import ResolvedProto, getResolvedProto
from Classes.SourceTextsByPath import SourceTextsByPath
from Classes.GeneratedHeaders import getSymbols
from Classes.Symbols import Symbols
from globals import SOURCE_EXTENSIONS
from strigify.setHeaderPath import set_entry_header_paths
from utils import normalize_excluded_paths


@dataclass(slots=True)
class TraversalResult:
    proto: ResolvedProto
    symbols: Symbols
    source_texts_by_path: SourceTextsByPath

    def usage_pattern_for_proto(self, proto_type: str | None, symbol_name: str | None) -> re.Pattern[str] | None:
        if not proto_type or not symbol_name:
            return None
        escaped_symbol_name = re.escape(symbol_name)
        if proto_type in {"function", "macro"}:
            return re.compile(rf"\b{escaped_symbol_name}\b\s*(?=\()")
        return re.compile(rf"\b{escaped_symbol_name}\b")

    def countProtoUsage(self, proto_match: ProtoMatch, source_text: str) -> int:
        usage_pattern = self.usage_pattern_for_proto(proto_match.proto_type, proto_match.symbol_name)
        if usage_pattern is None:
            return 0
        return len(usage_pattern.findall(source_text))

    def setRecurence(self) -> "TraversalResult":
        for source_path, source_text in self.source_texts_by_path.items():
            for proto_match in self.symbols.values():
                recurence = self.countProtoUsage(proto_match, source_text)
                if recurence > 0:
                    proto_match.recurence[source_path] = proto_match.recurence.get(source_path, 0) + recurence
        return self

    def correctIncludeSet(self, include_set: set[str]) -> set[str]:
        for symbol in self.symbols.values():
            if symbol.header_path is None:
                continue
            include_path = Path(symbol.header_path)
            include_set.discard(symbol.header_path)
            include_set.discard(include_path.name)
            include_set.discard(f'"{include_path.name}"')
            include_set.discard(f"<{include_path.name}>")
        return include_set


def getTraversalResult(
    startPath: str,
    excludedFolderPath: list[str],
    source_texts_by_path: SourceTextsByPath,
) -> TraversalResult:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath)
    source_extensions = SOURCE_EXTENSIONS
    protos = getResolvedProto(startPath, source_extensions, excludedFolderPath)
    symbols = getSymbols(
        start_path,
        excluded_paths,
        source_extensions,
        protos,
    )
    set_entry_header_paths(symbols)
    return TraversalResult(
        proto=protos,
        symbols=symbols,
        source_texts_by_path=source_texts_by_path,
    )
