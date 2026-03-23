#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Any

from srcs.script.generateJson import read_config_entries, write_config_entries
from srcs.script.utils import getEntryByIndex

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set one compile profile flags entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Set the entry at this index.",
    )
    parser.add_argument(
        "profile_index",
        type=int,
        help="Set the compile profile at this index.",
    )
    parser.add_argument(
        "new_flags",
        nargs=argparse.REMAINDER,
        help="New compile flags string.",
    )
    return parser.parse_args()


def getCompileProfile(entry: dict[str, Any], profile_index: int) -> dict[str, Any]:
    compile_profiles = entry.get("compile_profiles")
    if not isinstance(compile_profiles, list) or not compile_profiles:
        raise SystemExit("Selected entry does not contain any compile profiles.")
    if profile_index < 0 or profile_index >= len(compile_profiles):
        raise SystemExit(f"Compile profile index {profile_index} is out of range.")
    profile = compile_profiles[profile_index]
    if not isinstance(profile, dict):
        raise SystemExit(f"Compile profile at index {profile_index} is invalid.")
    return profile


def setCompileFlagsForProfile() -> None:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)
    compile_profile = getCompileProfile(entry, args.profile_index)
    new_flags = " ".join(args.new_flags)

    previous_flags = compile_profile.get("flags", "")
    compile_profile["flags"] = new_flags
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(
        f"Updated compile profile flags for entry {args.entry_index}, profile {args.profile_index}: "
        f"{previous_flags!r} -> {new_flags!r}"
    )


if __name__ == "__main__":
    setCompileFlagsForProfile()
