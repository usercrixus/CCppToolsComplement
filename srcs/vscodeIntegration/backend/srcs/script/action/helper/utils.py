#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Any


def getProgramNameFromMakefileName(output_makefile: Path) -> str | None:
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


def readJsonObject(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    if not isinstance(data, dict):
        return default
    return data


def writeJsonObject(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def compiler_var_key(compiler: str) -> str:
    explicit = {"g++": "GPP", "gcc": "GCC"}
    if compiler in explicit:
        return explicit[compiler]
    key = re.sub(r"[^A-Za-z0-9]+", "_", compiler).strip("_").upper()
    return key or "CC"


def getCompiler(ext: str) -> str:
    if ext == ".c":
        return "gcc"
    if ext in {".cpp", ".cc", ".cxx"}:
        return "g++"
    raise ValueError(f"Unsupported main extension: {ext}")
