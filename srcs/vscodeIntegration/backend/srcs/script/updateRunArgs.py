#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the run_args field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Update the entry at this index.",
    )
    parser.add_argument(
        "new_args",
        nargs=argparse.REMAINDER,
        help="New run arguments string.",
    )
    return parser.parse_args()

def updateRunArgs() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    new_args = " ".join(args.new_args)

    previous_run_args = entry.get("run_args", "")
    entry["run_args"] = new_args
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated run_args for entry {args.entry_index}: "
        f"{previous_run_args!r} -> {new_args!r}"
    )


if __name__ == "__main__":
    updateRunArgs()
