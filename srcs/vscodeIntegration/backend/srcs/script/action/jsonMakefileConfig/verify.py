#!/usr/bin/env python3
import json
from pathlib import Path

from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.exception.exceptionJsonErrorsList import JsonValidationError

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def getEntryErrors(data: object) -> tuple[list[MakefileConfigEntry], list[str]]:
    if not isinstance(data, list):
        return [], ["JSON root must be an array."]

    entries: list[MakefileConfigEntry] = []
    errors: list[str] = []
    for entry_index, entry_data in enumerate(data):
        try:
            entries.append(MakefileConfigEntry.fromJsonObject(entry_data))
        except JsonValidationError as error:
            errors.extend(
                [f"[entry {entry_index}] {message}" for message in error.errors]
            )
    return entries, errors


def getEntries(config_path: Path) -> tuple[list[MakefileConfigEntry], list[str]]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"Invalid JSON in {config_path}: {exc}"]
    except OSError as exc:
        return [], [f"Unable to read JSON file {config_path}: {exc}"]
    return getEntryErrors(data)


def printSummary(errors: list[str], config_path: Path, entries: list[MakefileConfigEntry]) -> None:
    if errors:
        print(f"Verification failed for {config_path}:")
        for error in errors:
            print(f"- {error}")
        return
    print(f"Verification passed for {config_path} ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}).")


def verifyJson() -> int:
    config_path = Path.cwd() / CONFIG_REL_PATH
    entries, errors = getEntries(config_path.resolve())
    printSummary(errors, config_path.resolve(), entries)
    return 1 if errors else 0


def verifyjson() -> int:
    return verifyJson()


if __name__ == "__main__":
    raise SystemExit(verifyJson())
