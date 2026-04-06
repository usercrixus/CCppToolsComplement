from __future__ import annotations
from typing import TypeAlias
from Classes.Header import Header
from Classes.ProtoMatch import ProtoMatch

Symbols: TypeAlias = dict[str, ProtoMatch]
Headers: TypeAlias = dict[str, Header]
IncludeMap: TypeAlias = dict[str, set[str]]
