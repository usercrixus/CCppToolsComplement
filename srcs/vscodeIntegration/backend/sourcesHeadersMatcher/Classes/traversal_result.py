from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from Classes.proto_match import ProtoMatch
from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import SourceTextsByPath
from generatedHeaders import GeneratedHeaders, getGeneratedHeaders
from getResolvedProto import getResolvedProto
from globals import C_SOURCE_EXTENSIONS, CPP_SOURCE_EXTENSIONS
from utils import normalize_excluded_paths


@dataclass(slots=True)
class TraversalResult:
    proto: ResolvedProto
    generated_headers: GeneratedHeaders
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
            for proto_matches in self.generated_headers.values():
                if not proto_matches:
                    continue
                recurence = self.countProtoUsage(proto_matches[0], source_text)
                if recurence > 0:
                    for proto_match in proto_matches:
                        proto_match.recurence[source_path] = proto_match.recurence.get(source_path, 0) + recurence
        return self


def getTraversalResult(
    startPath: str,
    excludedFolderPath: list[str],
    source_texts_by_path: SourceTextsByPath,
) -> TraversalResult:
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath)
    source_extensions = C_SOURCE_EXTENSIONS | CPP_SOURCE_EXTENSIONS
    protos = getResolvedProto(startPath, source_extensions, excludedFolderPath)
    generated_headers = getGeneratedHeaders(
        start_path,
        excluded_paths,
        source_extensions,
        protos,
    )
    return TraversalResult(
        proto=protos,
        generated_headers=generated_headers,
        source_texts_by_path=source_texts_by_path,
    )
