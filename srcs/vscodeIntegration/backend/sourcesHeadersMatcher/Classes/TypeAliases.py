from __future__ import annotations
from typing import TypeAlias

from Classes.Header import Header

Headers: TypeAlias = dict[str, Header]
IncludeMap: TypeAlias = dict[str, set[str]]
