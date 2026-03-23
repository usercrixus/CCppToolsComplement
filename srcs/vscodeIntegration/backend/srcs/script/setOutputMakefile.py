#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set the output_makefile field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "output_makefile",
        help="New output Makefile path.",
    )
    return parser.parse_args()


def setOutputMakefile() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)

    previous_output_makefile = entry.get("output_makefile", "")
    entry["output_makefile"] = args.output_makefile
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated output_makefile for entry {args.entry_index}: "
        f"{previous_output_makefile!r} -> {args.output_makefile!r}"
    )


if __name__ == "__main__":
    setOutputMakefile()
