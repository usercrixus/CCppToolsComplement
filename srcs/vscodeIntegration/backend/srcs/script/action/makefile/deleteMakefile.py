#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path

from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.MakefileConfigEntry.utils import readEntries
from srcs.script.action.makefile.generateMakefile import getProgramsForDirectory, renderParentMakefile

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete one makefile from .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Delete the makefile for the entry at this index.",
    )
    return parser.parse_args()


def getEntryByIndex(entries: list[MakefileConfigEntry], entry_index: int) -> MakefileConfigEntry:
    if not entries:
        raise ValueError("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise ValueError(f"Entry index {entry_index} is out of range.")
    return entries[entry_index]


def deleteMakefile(entry_index: int) -> None:
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    entry = getEntryByIndex(entries, entry_index)
    output_makefile = (workspace_root / entry.output_makefile).resolve()
    parent_directory = output_makefile.parent

    if output_makefile.exists() and output_makefile.is_file():
        subprocess.run(
            ["make", "-f", output_makefile.name, "fclean"],
            cwd=parent_directory,
            check=True,
        )
        output_makefile.unlink()
        print(f"Deleted {output_makefile}")

    remaining_entries = [candidate for index, candidate in enumerate(entries) if index != entry_index]
    parent_makefile = parent_directory / "Makefile"
    programs = getProgramsForDirectory(remaining_entries, parent_directory, workspace_root)

    if not programs:
        if parent_makefile.exists() and parent_makefile.is_file():
            parent_makefile.unlink()
            print(f"Deleted {parent_makefile}")
        return

    parent_makefile.write_text(renderParentMakefile(programs), encoding="utf-8")
    print(f"Updated parent {parent_makefile}")


if __name__ == "__main__":
    deleteMakefile(parse_args().entry_index)
