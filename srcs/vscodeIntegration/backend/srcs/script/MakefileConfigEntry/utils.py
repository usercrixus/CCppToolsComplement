import json
from pathlib import Path
from typing import Any

from srcs.script.MakefileConfigEntry.CompileProfile import CompileProfile
from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry


def makeEmptyCompileProfile() -> CompileProfile:
    return CompileProfile()


def makeEmptyMakefileConfigEntry() -> MakefileConfigEntry:
    return MakefileConfigEntry()


def parseMakefileConfigEntries(data: Any) -> list[MakefileConfigEntry]:
    if not isinstance(data, list):
        raise ValueError("makefile config must be a JSON array")
    return [MakefileConfigEntry.fromJsonObject(entry_data) for entry_data in data]


def parseMakefileConfigEntriesJson(json_text: str) -> list[MakefileConfigEntry]:
    return parseMakefileConfigEntries(json.loads(json_text))


def readEntries(config_path: Path) -> list[MakefileConfigEntry]:
    if not config_path.exists():
        return []
    return parseMakefileConfigEntriesJson(config_path.read_text(encoding="utf-8"))


def upsertEntry(entries: list[MakefileConfigEntry], next_entry: MakefileConfigEntry) -> list[MakefileConfigEntry]:
    result: list[MakefileConfigEntry] = []
    replaced = False
    for entry in entries:
        if entry.output_makefile == next_entry.output_makefile:
            result.append(next_entry)
            replaced = True
            continue
        result.append(entry)
    if not replaced:
        result.append(next_entry)
    return result


def writeEntries(config_path: Path, entries: list[MakefileConfigEntry]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(makefileConfigEntriesToJson(entries) + "\n", encoding="utf-8")


def makefileConfigEntriesToJsonObject(entries: list[MakefileConfigEntry]) -> list[dict[str, Any]]:
    return [entry.toJsonObject() for entry in entries]


def makefileConfigEntriesToJson(entries: list[MakefileConfigEntry]) -> str:
    return json.dumps(makefileConfigEntriesToJsonObject(entries), indent=2)
