#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the link_flags field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Update the entry at this index.",
    )
    parser.add_argument(
        "new_link_flags",
        nargs=argparse.REMAINDER,
        help="New link flags string.",
    )
    return parser.parse_args()


def updateLinkFlags() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    new_link_flags = " ".join(args.new_link_flags)

    previous_link_flags = entry.get("link_flags", "")
    entry["link_flags"] = new_link_flags
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated link_flags for entry {args.entry_index}: "
        f"{previous_link_flags!r} -> {new_link_flags!r}"
    )


if __name__ == "__main__":
    updateLinkFlags()
