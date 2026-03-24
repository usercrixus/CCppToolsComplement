#!/usr/bin/env python3
import shlex
from pathlib import Path
from typing import Any

from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.MakefileConfigEntry.utils import readEntries
from srcs.script.action.helper.utils import getProgramNameFromMakefileName, readJsonObject, writeJsonObject
from srcs.script.action.helper.verifyJson import verifyJson

JsonObject = dict[str, Any]
JsonItems = list[JsonObject]
LAUNCH_REL_PATH = Path(".vscode/launch.json")


def splitArgs(value: str) -> list[str]:
    stripped = value.strip()
    if not stripped:
        return []
    try:
        return shlex.split(stripped)
    except ValueError:
        return [stripped]


def mergeByKey(existing: JsonItems, generated: JsonItems, key: str) -> JsonItems:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    merged: JsonItems = []
    for item in generated:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
            continue
        seen.add(item_key)
        merged.append(item)
    for item in existing:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
            continue
        seen.add(item_key)
        merged.append(item)
    for item_key in duplicates:
        print(f"Multiple items with key {item_key!r}; kept the first occurrence.")
    return merged


def vscodePathForFsPath(path: Path, workspace: Path) -> str:
    rel = path.relative_to(workspace).as_posix()
    if rel == ".":
        return "${workspaceFolder}"
    return f"${{workspaceFolder}}/{rel}"


def getProgramName(entry: MakefileConfigEntry) -> str:
    output_makefile = Path(entry.output_makefile)
    program_name = getProgramNameFromMakefileName(output_makefile)
    if not program_name:
        raise ValueError(f"Invalid output_makefile for entry: {entry.output_makefile!r}")
    return program_name


def makeLaunch(entry: MakefileConfigEntry, workspace: Path) -> JsonObject:
    output_makefile = (workspace / entry.output_makefile).resolve()
    program_name = getProgramName(entry)
    cwd_vscode = vscodePathForFsPath(output_makefile.parent, workspace)
    program_vscode = vscodePathForFsPath(output_makefile.parent / entry.bin_name, workspace)
    return {
        "name": program_name,
        "type": "cppdbg",
        "request": "launch",
        "program": program_vscode,
        "args": splitArgs(entry.run_args),
        "stopAtEntry": False,
        "cwd": cwd_vscode,
        "environment": [],
        "externalConsole": False,
        "MIMode": "gdb",
        "miDebuggerPath": "/usr/bin/gdb",
        "preLaunchTask": f"build {program_name} (debug)",
        "setupCommands": [
            {
                "description": "Enable pretty-printing for gdb",
                "text": "-enable-pretty-printing",
                "ignoreFailures": True,
            }
        ],
    }


def generateLaunch() -> None:
    if verifyJson() != 0:
        raise SystemExit("Makefile configuration verification failed.")
    workspace = Path.cwd().resolve()
    launch_path = (workspace / LAUNCH_REL_PATH).resolve()
    config_path = (workspace / ".vscode/makefileConfig.json").resolve()
    entries = readEntries(config_path)
    generated_launches = [makeLaunch(entry, workspace) for entry in entries]
    launch_json = readJsonObject(launch_path, {"version": "0.2.0", "configurations": []})
    existing_configurations = launch_json.get("configurations", [])
    if not isinstance(existing_configurations, list):
        existing_configurations = []
    launch_json["version"] = launch_json.get("version", "0.2.0")
    launch_json["configurations"] = mergeByKey(
        [item for item in existing_configurations if isinstance(item, dict)],
        generated_launches,
        "name",
    )
    writeJsonObject(launch_path, launch_json)
    print(f"Generated {launch_path}")


if __name__ == "__main__":
    generateLaunch()
