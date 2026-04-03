from __future__ import annotations

from Classes.resolved_proto import ResolvedProto
from Classes.type_aliases import GeneratedHeaders, SourceTextsByPath
from protoImplementationMatcher import build_proto_map


def generateHeader(
    filePath: str,
    proto: ResolvedProto,
    source_text: str,
    source_texts_by_path: SourceTextsByPath | None = None,
) -> GeneratedHeaders:
    return build_proto_map(filePath, proto, source_text, source_texts_by_path or {})
