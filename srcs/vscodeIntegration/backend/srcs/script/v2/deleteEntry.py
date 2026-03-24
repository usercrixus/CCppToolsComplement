#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from srcs.script.v2.jsonModel import (
    MakefileConfigEntry,
    makefileConfigEntriesToJson,
    parseMakefileConfigEntriesJson,
)
from srcs.script.v2.utils import getProgramNameFromMakefileName

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")
TASKS_REL_PATH = Path(".vscode/tasks.json")
LAUNCH_REL_PATH = Path(".vscode/launch.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove one entry from .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Delete the entry at this index.",
    )
    return parser.parse_args()


def readEntries(config_path: Path) -> list[MakefileConfigEntry]:
    if not config_path.exists():
        raise ValueError(f"No config file found at {config_path}")
    return parseMakefileConfigEntriesJson(config_path.read_text(encoding="utf-8"))


def writeEntries(config_path: Path, entries: list[MakefileConfigEntry]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(makefileConfigEntriesToJson(entries) + "\n", encoding="utf-8")


def deleteEntryAtIndex(entries: list[MakefileConfigEntry], entry_index: int) -> MakefileConfigEntry:
    if not entries:
        raise ValueError("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise ValueError(f"Entry index {entry_index} is out of range.")
    return entries.pop(entry_index)


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
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def getProgramName(entry: MakefileConfigEntry) -> str | None:
    if not entry.output_makefile.strip():
        return None
    return getProgramNameFromMakefileName(Path(entry.output_makefile))


def deleteTaskEntry(program_name: str, workspace_root: Path) -> None:
    tasks_path = (workspace_root / TASKS_REL_PATH).resolve()
    tasks_json = readJsonObject(tasks_path, {"version": "2.0.0", "tasks": []})
    tasks = tasks_json.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
    task_label = f"build {program_name} (debug)"
    tasks_json["tasks"] = [
        task for task in tasks if not (isinstance(task, dict) and task.get("label") == task_label)
    ]
    writeJsonObject(tasks_path, tasks_json)
    print(f"Updated {tasks_path}")


def deleteLaunchEntry(program_name: str, workspace_root: Path) -> None:
    launch_path = (workspace_root / LAUNCH_REL_PATH).resolve()
    launch_json = readJsonObject(launch_path, {"version": "0.2.0", "configurations": []})
    configurations = launch_json.get("configurations", [])
    if not isinstance(configurations, list):
        configurations = []
    launch_json["configurations"] = [
        configuration
        for configuration in configurations
        if not (isinstance(configuration, dict) and configuration.get("name") == program_name)
    ]
    writeJsonObject(launch_path, launch_json)
    print(f"Updated {launch_path}")


def main() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    removed_entry = deleteEntryAtIndex(entries, args.entry_index)
    writeEntries(config_path, entries)

    print(f"Updated {config_path}")
    print(f"Removed entry at index {args.entry_index}")

    program_name = getProgramName(removed_entry)
    if program_name:
        deleteTaskEntry(program_name, workspace_root)
        deleteLaunchEntry(program_name, workspace_root)


if __name__ == "__main__":
    main()
