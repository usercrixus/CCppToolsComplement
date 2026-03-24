#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.MakefileConfigEntry.utils import (
    readEntries,
    writeEntries,
)

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


def deleteEntryAtIndex(entries: list[MakefileConfigEntry], entry_index: int) -> MakefileConfigEntry:
    if not entries:
        raise ValueError("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise ValueError(f"Entry index {entry_index} is out of range.")
    return entries.pop(entry_index)


def main() -> None:
    args = parse_args()
    config_path = (Path.cwd().resolve() / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    deleteEntryAtIndex(entries, args.entry_index)
    writeEntries(config_path, entries)

    print(f"Updated {config_path}")
    print(f"Removed entry at index {args.entry_index}")


if __name__ == "__main__":
    main()
