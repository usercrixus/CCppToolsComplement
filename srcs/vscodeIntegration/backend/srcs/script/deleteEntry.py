#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


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
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    if not entries:
        raise SystemExit(f"No program entries found in {config_path}")

    if args.entry_index < 0 or args.entry_index >= len(entries):
        raise SystemExit(f"Entry index {args.entry_index} is out of range.")

    entries.pop(args.entry_index)
    write_config_entries(config_path, entries)
    print(f"Updated {config_path}")
    print(f"Removed entry at index {args.entry_index}")


if __name__ == "__main__":
    deleteEntry()
