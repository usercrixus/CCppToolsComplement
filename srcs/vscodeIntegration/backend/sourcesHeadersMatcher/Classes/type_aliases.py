from __future__ import annotations
from typing import TypeAlias
from Classes.proto_match import ProtoMatch

GeneratedHeaders: TypeAlias = dict[str, list[ProtoMatch]]
SourceTextsByPath: TypeAlias = dict[str, str]
HeaderMap: TypeAlias = dict[str, list[str]]
IncludeMap: TypeAlias = dict[str, set[str]]
