#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from srcs.script.v2.jsonModel import (
    CompileProfile,
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
        "--output-makefile",
        help="New output Makefile path.",
    )
    parser.add_argument(
        "--compile-profiles-json",
        help="New compile_profiles JSON array.",
    )
    parser.add_argument(
        "--link-compiler",
        help="New link compiler.",
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
        "--bin-name",
        help="New binary name.",
    )
    parser.add_argument(
        "--rel-sources-json",
        help="New rel_sources JSON array.",
    )
    parser.add_argument(
        "--obj-expr",
        help="New object expression.",
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


def parseCompileProfilesJson(json_text: str) -> list[CompileProfile]:
    data = json.loads(json_text)
    if not isinstance(data, list):
        raise ValueError("compile_profiles must be a JSON array")
    return [CompileProfile.fromJsonObject(item) for item in data]


def parseRelSourcesJson(json_text: str) -> list[str]:
    data = json.loads(json_text)
    if not isinstance(data, list):
        raise ValueError("rel_sources must be a JSON array")
    return [str(item) for item in data]


def updateEntry(entry: MakefileConfigEntry, args: argparse.Namespace) -> None:
    if args.output_makefile is not None:
        entry.setOutputMakefile(args.output_makefile)
    if args.rel_sources_json is not None:
        entry.setRelSources(parseRelSourcesJson(args.rel_sources_json))
    if args.compile_profiles_json is not None:
        entry.setCompileProfiles(parseCompileProfilesJson(args.compile_profiles_json))
    if args.link_compiler is not None:
        entry.setLinkCompiler(args.link_compiler)
    if args.link_flags is not None:
        entry.setLinkFlags(args.link_flags)
    if args.run_args is not None:
        entry.setRunArgs(args.run_args)
    if args.bin_name is not None:
        entry.setBinName(args.bin_name)
    if args.obj_expr is not None:
        entry.setObjExpr(args.obj_expr)


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
