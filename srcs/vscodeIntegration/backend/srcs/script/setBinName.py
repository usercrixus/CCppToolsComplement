#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set the bin_name field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "bin_name",
        help="New binary name.",
    )
    return parser.parse_args()


def setBinName() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)

    previous_bin_name = entry.get("bin_name", "")
    entry["bin_name"] = args.bin_name
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated bin_name for entry {args.entry_index}: "
        f"{previous_bin_name!r} -> {args.bin_name!r}"
    )


if __name__ == "__main__":
    setBinName()
