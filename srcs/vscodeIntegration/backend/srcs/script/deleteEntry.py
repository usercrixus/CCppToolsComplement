#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getProgramNameFromMakefileName

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")
TASKS_REL_PATH = Path(".vscode/tasks.json")
LAUNCH_REL_PATH = Path(".vscode/launch.json")


def read_json_object(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    if not isinstance(data, dict):
        return default
    return data


def write_json_object(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def get_program_name(entry: dict[str, Any]) -> str | None:
    output_makefile = entry.get("output_makefile")
    if not isinstance(output_makefile, str) or not output_makefile.strip():
        return None
    return getProgramNameFromMakefileName(Path(output_makefile))


def delete_removed_makefile(entry: dict[str, Any], workspace_root: Path) -> None:
    output_makefile = entry.get("output_makefile")
    if not isinstance(output_makefile, str) or not output_makefile.strip():
        return
    makefile_path = (workspace_root / output_makefile).resolve()
    if not makefile_path.exists() or not makefile_path.is_file():
        return
    makefile_path.unlink()
    print(f"Deleted {makefile_path}")


def delete_task_entry(program_name: str, workspace_root: Path) -> None:
    tasks_path = (workspace_root / TASKS_REL_PATH).resolve()
    tasks_json = read_json_object(tasks_path, {"version": "2.0.0", "tasks": []})
    tasks = tasks_json.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []
    task_label = f"build {program_name} (debug)"
    tasks_json["tasks"] = [
        task for task in tasks if not (isinstance(task, dict) and task.get("label") == task_label)
    ]
    write_json_object(tasks_path, tasks_json)
    print(f"Updated {tasks_path}")


def delete_launch_entry(program_name: str, workspace_root: Path) -> None:
    launch_path = (workspace_root / LAUNCH_REL_PATH).resolve()
    launch_json = read_json_object(launch_path, {"version": "0.2.0", "configurations": []})
    configurations = launch_json.get("configurations", [])
    if not isinstance(configurations, list):
        configurations = []
    launch_name = program_name
    launch_json["configurations"] = [
        configuration
        for configuration in configurations
        if not (isinstance(configuration, dict) and configuration.get("name") == launch_name)
    ]
    write_json_object(launch_path, launch_json)
    print(f"Updated {launch_path}")


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


def deleteEntry() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    if not entries:
        raise SystemExit(f"No program entries found in {config_path}")

    if args.entry_index < 0 or args.entry_index >= len(entries):
        raise SystemExit(f"Entry index {args.entry_index} is out of range.")

    removed_entry = entries.pop(args.entry_index)
    write_config_entries(config_path, entries)
    print(f"Updated {config_path}")
    print(f"Removed entry at index {args.entry_index}")
    delete_removed_makefile(removed_entry, workspace_root)

    program_name = get_program_name(removed_entry)
    if program_name:
        delete_task_entry(program_name, workspace_root)
        delete_launch_entry(program_name, workspace_root)


if __name__ == "__main__":
    deleteEntry()
