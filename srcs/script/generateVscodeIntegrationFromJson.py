#!/usr/bin/env python3
import argparse
import json
import shlex
from pathlib import Path
from typing import Any

from srcs.script.verifyJson import verifyjson
from srcs.script.utils import read_entries, getProgramNameFromMakefileName

JsonObject = dict[str, Any]
JsonItems = list[JsonObject]


def split_args(value: str) -> list[str]:
    stripped = value.strip()
    if not stripped:
        return []
    try:
        return shlex.split(stripped)
    except ValueError:
        return [stripped]


def read_json_or_default(path: Path, default: JsonObject) -> JsonObject:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return default
    if not isinstance(data, dict):
        return default
    return data


def merge_by_key(existing: JsonItems, generated: JsonItems, key: str) -> JsonItems:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    merged: JsonItems = []
    for item in generated:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
        else:
            seen.add(item_key)
            merged.append(item)
    for item in existing:
        item_key = item.get(key)
        if item_key in seen:
            duplicates.add(item_key)
        else:
            seen.add(item_key)
            merged.append(item)
    for item_key in duplicates:
        print(f"Multiple items with key {item_key!r}; kept the first occurrence.")
    return merged


def vscode_path_for_fs_path(path: Path, workspace: Path) -> str:
    rel = path.relative_to(workspace).as_posix()
    if rel == ".":
        return "${workspaceFolder}"
    return f"${{workspaceFolder}}/{rel}"


def make_task(program: str, output_makefile: Path, cwd_vscode: str) -> JsonObject:
    return {
        "label": f"graph: build {program} (debug)",
        "type": "shell",
        "command": "make",
        "args": ["-f", output_makefile.name, "all"],
        "options": {"cwd": cwd_vscode},
        "problemMatcher": ["$gcc"],
    }


def make_launch(program: str, launch_args: list[str], program_vscode: str, cwd_vscode: str) -> JsonObject:
    return {
        "name": f"Debug graph {program}",
        "type": "cppdbg",
        "request": "launch",
        "program": program_vscode,
        "args": launch_args,
        "stopAtEntry": False,
        "cwd": cwd_vscode,
        "environment": [],
        "externalConsole": False,
        "MIMode": "gdb",
        "miDebuggerPath": "/usr/bin/gdb",
        "preLaunchTask": f"graph: build {program} (debug)",
        "setupCommands": [
            {
                "description": "Enable pretty-printing for gdb",
                "text": "-enable-pretty-printing",
                "ignoreFailures": True,
            }
        ],
    }


def get_relevant_paths() -> tuple[Path, Path, Path, Path]:
    workspace = Path.cwd().resolve()
    vscode_dir = workspace / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    config_path = vscode_dir / "makefileConfig.json"
    tasks_path = vscode_dir / "tasks.json"
    launch_path = vscode_dir / "launch.json"
    return workspace, config_path, tasks_path, launch_path


def get_merged_json_version(
    path: Path, generated_items: JsonItems, version: str, collection_key: str, merge_key: str
) -> JsonObject:
    existing_json = read_json_or_default(path, {"version": version, collection_key: []})
    existing_items = existing_json.get(collection_key, [])
    if not isinstance(existing_items, list):
        existing_items = []
    return {
        "version": existing_json.get("version", version),
        collection_key: merge_by_key(
            [item for item in existing_items if isinstance(item, dict)], generated_items, merge_key
        ),
    }


def get_tasks_and_launches_from_config(workspace: Path, config_path: Path) -> tuple[JsonItems, JsonItems]:
    entries = read_entries(config_path)
    tasks: JsonItems = []
    launches: JsonItems = []
    for entry in entries:
        output_makefile = Path(str(entry.get("output_makefile", ""))).resolve()
        bin_name = str(entry.get("bin_name", ""))
        run_args = str(entry.get("run_args", ""))
        program = getProgramNameFromMakefileName(output_makefile) or ""
        cwd_vscode = vscode_path_for_fs_path(output_makefile.parent, workspace)
        program_vscode = vscode_path_for_fs_path(output_makefile.parent / bin_name, workspace)
        tasks.append(make_task(program, output_makefile, cwd_vscode))
        launches.append(make_launch(program, split_args(run_args), program_vscode, cwd_vscode))
    return tasks, launches


def generateVscodeIntegrationFromJson() -> None:
    if verifyjson() != 0:
        raise SystemExit("Makefile configuration verification failed.")
    workspace, config_path, tasks_path, launch_path = get_relevant_paths()
    tasks, launches = get_tasks_and_launches_from_config(workspace, config_path)
    tasks_json = get_merged_json_version(tasks_path, tasks, "2.0.0", "tasks", "label")
    launch_json = get_merged_json_version(launch_path, launches, "0.2.0", "configurations", "name")
    tasks_path.write_text(json.dumps(tasks_json, indent=2) + "\n", encoding="utf-8")
    launch_path.write_text(json.dumps(launch_json, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {tasks_path}")
    print(f"Generated {launch_path}")


if __name__ == "__main__":
    generateVscodeIntegrationFromJson()
