#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from srcs.script.v2.jsonModel import (
    MakefileConfigEntry,
    makefileConfigEntriesToJson,
    parseMakefileConfigEntriesJson,
)

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


def readEntries(config_path: Path) -> list[MakefileConfigEntry]:
    if not config_path.exists():
        raise ValueError(f"No config file found at {config_path}")
    return parseMakefileConfigEntriesJson(config_path.read_text(encoding="utf-8"))


def writeEntries(config_path: Path, entries: list[MakefileConfigEntry]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(makefileConfigEntriesToJson(entries) + "\n", encoding="utf-8")


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


def setCompileProfileFlags(entry: MakefileConfigEntry, profile_index: int, flags: str) -> None:
    if profile_index < 0 or profile_index >= len(entry.compile_profiles):
        raise ValueError(f"Compile profile index {profile_index} is out of range.")
    entry.compile_profiles[profile_index].setFlags(flags)


def updateEntry(entry: MakefileConfigEntry, args: argparse.Namespace) -> None:
    if args.rel_sources_json is not None:
        entry.setRelSources(parseRelSourcesJson(args.rel_sources_json))
    if args.link_flag_compile_profiles is not None:
        if args.compile_profile_index is None:
            raise ValueError("--compile-profile-index is required with --link-flag-compile-profiles")
        setCompileProfileFlags(entry, args.compile_profile_index, args.link_flag_compile_profiles)
    if args.link_flags is not None:
        entry.setLinkFlags(args.link_flags)
    if args.run_args is not None:
        entry.setRunArgs(args.run_args)


def main() -> None:
    args = parse_args()
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    previous_entry: dict[str, Any] = entry.toJsonObject()
    updateEntry(entry, args)
    writeEntries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated entry {args.entry_index}: "
        f"{json.dumps(previous_entry, sort_keys=True)} -> {json.dumps(entry.toJsonObject(), sort_keys=True)}"
    )


if __name__ == "__main__":
    main()
