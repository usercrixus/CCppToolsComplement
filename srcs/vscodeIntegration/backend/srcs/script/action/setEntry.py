#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any

from srcs.script.action.helper.getRelSources import getRelSources
from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.MakefileConfigEntry.utils import (
    readEntries,
    writeEntries,
)
from srcs.script.action.helper.utils import getProgramNameFromMakefileName

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set one entry fields in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "--link-flag-compile-profiles",
        help="New flags value for one compile profile.",
    )
    parser.add_argument(
        "--compile-profile-index",
        type=int,
        help="Compile profile index to update.",
    )
    parser.add_argument(
        "--link-flags",
        help="New link flags.",
    )
    parser.add_argument(
        "--run-args",
        help="New run arguments string.",
    )
    parser.add_argument(
        "--rel-sources-json",
        help="New rel_sources JSON array.",
    )
    return parser.parse_args()
def getEntryByIndex(entries: list[MakefileConfigEntry], entry_index: int) -> MakefileConfigEntry:
    if not entries:
        raise ValueError("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise ValueError(f"Entry index {entry_index} is out of range.")
    return entries[entry_index]


def parseRelSourcesJson(json_text: str) -> list[str]:
    data = json.loads(json_text)
    if not isinstance(data, list):
        raise ValueError("rel_sources must be a JSON array")
    return [str(item) for item in data]


def rebuildRelSources(entry: MakefileConfigEntry, rel_sources: list[str]) -> list[str]:
    if not rel_sources:
        raise ValueError("rel_sources must contain at least one source path")
    project_root = Path.cwd().resolve()
    output_makefile_path = (project_root / entry.output_makefile).resolve()
    program_name = getProgramNameFromMakefileName(output_makefile_path)
    if not program_name:
        raise ValueError(f"Invalid output_makefile for entry: {entry.output_makefile!r}")
    main_source_path = (output_makefile_path.parent / rel_sources[0]).resolve()
    return getRelSources(str(main_source_path), program_name, project_root)


def setCompileProfileFlags(entry: MakefileConfigEntry, profile_index: int, flags: str) -> None:
    if profile_index < 0 or profile_index >= len(entry.compile_profiles):
        raise ValueError(f"Compile profile index {profile_index} is out of range.")
    entry.compile_profiles[profile_index].setFlags(flags)


def updateEntry(entry: MakefileConfigEntry, args: argparse.Namespace) -> int:
    refresh_status = 0
    if args.rel_sources_json is not None:
        previous_compilers = {profile.compiler for profile in entry.compile_profiles if profile.compiler}
        entry.setRelSources(rebuildRelSources(entry, parseRelSourcesJson(args.rel_sources_json)))
        next_compilers = {profile.compiler for profile in entry.compile_profiles if profile.compiler}
        refresh_status = 1 if next_compilers - previous_compilers else 0
    if args.link_flag_compile_profiles is not None:
        if args.compile_profile_index is None:
            raise ValueError("--compile-profile-index is required with --link-flag-compile-profiles")
        setCompileProfileFlags(entry, args.compile_profile_index, args.link_flag_compile_profiles)
    if args.link_flags is not None:
        entry.setLinkFlags(args.link_flags)
    if args.run_args is not None:
        entry.setRunArgs(args.run_args)
    return refresh_status


def main() -> None:
    args = parse_args()
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    previous_entry: dict[str, Any] = entry.toJsonObject()
    refresh_status = updateEntry(entry, args)
    writeEntries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated entry {args.entry_index}: "
        f"{json.dumps(previous_entry, sort_keys=True)} -> {json.dumps(entry.toJsonObject(), sort_keys=True)}"
    )
    sys.exit(refresh_status)


if __name__ == "__main__":
    main()
