#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set the rel_sources field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "rel_sources",
        nargs=argparse.REMAINDER,
        help="New relative source paths.",
    )
    return parser.parse_args()


def setRelSources() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)

    previous_rel_sources = entry.get("rel_sources", [])
    entry["rel_sources"] = args.rel_sources
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated rel_sources for entry {args.entry_index}: "
        f"{previous_rel_sources!r} -> {args.rel_sources!r}"
    )


if __name__ == "__main__":
    setRelSources()
