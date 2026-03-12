#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any


def program_from_output_makefile(output_makefile: Path) -> str | None:
    prefix = "Makefile."
    if not output_makefile.name.startswith(prefix):
        return None
    program = output_makefile.name[len(prefix) :].strip()
    if not program or "." in program:
        return None
    return program


def read_entries(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in data if isinstance(item, dict)]
