#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

from srcs.script.v2.getRelSources import getRelSources
from srcs.script.v2.getRelSources import getMainPath, getOutputPath
from srcs.script.v2.jsonModel import (
    MakefileConfigEntry,
    makefileConfigEntriesToJson,
    parseMakefileConfigEntriesJson,
)

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build one MakefileConfigEntry from frontend generateJson-style args.",
    )
    parser.add_argument(
        "--main-path",
        required=True,
        help="Path to the main source file.",
    )
    parser.add_argument(
        "--program-name",
        required=True,
        help="Program name. Must match Makefile.<program>.",
    )
    parser.add_argument(
        "--run-args",
        default="",
        help="Run arguments string.",
    )
    parser.add_argument(
        "--bin-name",
        default="",
        help="Binary name. Defaults to <program>.out.",
    )
    return parser.parse_args()


def createLaunch(
    main_path_input: str, program_name: str, run_args: str = "", bin_name: str = ""
) -> MakefileConfigEntry:
    project_root = Path.cwd()
    main_path = getMainPath(main_path_input, project_root)
    output_makefile = os.path.relpath(
        getOutputPath(main_path, program_name),
        project_root,
    ).replace("\\", "/")
    entry = MakefileConfigEntry()
    entry.setOutputMakefile(output_makefile)
    entry.setRelSources(getRelSources(main_path_input, program_name, project_root))
    entry.setRunArgs(run_args)
    entry.setBinName(bin_name if bin_name else f"{program_name}.out")
    return entry


def readEntries(config_path: Path) -> list[MakefileConfigEntry]:
    if not config_path.exists():
        return []
    return parseMakefileConfigEntriesJson(config_path.read_text(encoding="utf-8"))


def upsertEntry(entries: list[MakefileConfigEntry], next_entry: MakefileConfigEntry) -> list[MakefileConfigEntry]:
    result: list[MakefileConfigEntry] = []
    replaced = False
    for entry in entries:
        if entry.output_makefile == next_entry.output_makefile:
            result.append(next_entry)
            replaced = True
            continue
        result.append(entry)
    if not replaced:
        result.append(next_entry)
    return result


def writeEntries(config_path: Path, entries: list[MakefileConfigEntry]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(makefileConfigEntriesToJson(entries) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    entry = createLaunch(
        args.main_path,
        args.program_name,
        args.run_args,
        args.bin_name,
    )
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    entries = upsertEntry(entries, entry)
    writeEntries(config_path, entries)


if __name__ == "__main__":
    main()
