#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.action.helper.utils import readJsonObject, writeJsonObject

TASKS_REL_PATH = Path(".vscode/tasks.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delete one generated task from .vscode/tasks.json.")
    parser.add_argument("program_name", help="Program name used in the generated task label.")
    return parser.parse_args()


def deleteTask(program_name: str) -> None:
    workspace = Path.cwd().resolve()
    tasks_path = (workspace / TASKS_REL_PATH).resolve()
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


if __name__ == "__main__":
    deleteTask(parse_args().program_name)
