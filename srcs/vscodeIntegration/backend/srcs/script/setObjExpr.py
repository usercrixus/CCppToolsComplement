#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set the obj_expr field of one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "obj_expr",
        nargs=argparse.REMAINDER,
        help="New object expression.",
    )
    return parser.parse_args()


def setObjExpr() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    new_obj_expr = " ".join(args.obj_expr)

    previous_obj_expr = entry.get("obj_expr", "")
    entry["obj_expr"] = new_obj_expr
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated obj_expr for entry {args.entry_index}: "
        f"{previous_obj_expr!r} -> {new_obj_expr!r}"
    )


if __name__ == "__main__":
    setObjExpr()
