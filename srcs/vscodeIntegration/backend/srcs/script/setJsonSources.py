#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Any

from srcs.script.generateJson import (
    CONFIG_REL_PATH,
    build_compile_profiles,
    detect_compilers_by_ext,
    getSource,
    getRelativePath,
    objs_from_sources,
    pick_linker_compiler,
    read_config_entries,
    write_config_entries,
)
from srcs.script.utils import getEntryByIndex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh rel_sources and compilers for one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Update the entry at this index.",
    )
    return parser.parse_args()


def getOutputMakefilePath(entry: dict[str, Any], workspace_root: Path) -> Path:
    output_makefile = entry.get("output_makefile")
    if not isinstance(output_makefile, str) or not output_makefile.strip():
        raise SystemExit("Selected entry is missing 'output_makefile'.")
    return (workspace_root / output_makefile).resolve()


def getMainPathFromEntry(entry: dict[str, Any], workspace_root: Path) -> Path:
    rel_sources = entry.get("rel_sources")
    if not isinstance(rel_sources, list) or not rel_sources:
        raise SystemExit("Selected entry does not contain any source files.")

    main_source = rel_sources[0]
    if not isinstance(main_source, str) or not main_source.strip():
        raise SystemExit("Selected entry has an invalid main source.")

    output_makefile_path = getOutputMakefilePath(entry, workspace_root)
    main_path = (output_makefile_path.parent / main_source).resolve()
    if not main_path.exists():
        raise SystemExit(f"Main file not found: {main_path}")
    return main_path


def getFlagsByCompiler(entry: dict[str, Any], compilers_by_ext: dict[str, str]) -> dict[str, str]:
    flags_by_compiler = {compiler: "" for compiler in set(compilers_by_ext.values())}
    compile_profiles = entry.get("compile_profiles")
    if not isinstance(compile_profiles, list):
        return flags_by_compiler

    for profile in compile_profiles:
        if not isinstance(profile, dict):
            continue
        compiler = profile.get("compiler")
        flags = profile.get("flags")
        if compiler in flags_by_compiler and isinstance(flags, str):
            flags_by_compiler[compiler] = flags
    return flags_by_compiler


def getCompilers(entry: dict[str, Any]) -> set[str]:
    compile_profiles = entry.get("compile_profiles")
    if not isinstance(compile_profiles, list):
        return set()
    compilers = set()
    for profile in compile_profiles:
        if not isinstance(profile, dict):
            continue
        compiler = profile.get("compiler")
        if isinstance(compiler, str) and compiler:
            compilers.add(compiler)
    return compilers


def setJsonSources() -> int:
    args = parse_args()
    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = read_config_entries(config_path)
    entry = getEntryByIndex(entries, args.entry_index)

    previous_compilers = getCompilers(entry)
    output_makefile_path = getOutputMakefilePath(entry, workspace_root)
    main_path = getMainPathFromEntry(entry, workspace_root)
    sources = getSource(main_path, workspace_root)
    relative_sources_path = getRelativePath(sources, output_makefile_path.parent)
    compilers_by_ext = detect_compilers_by_ext(relative_sources_path)
    compile_profiles = build_compile_profiles(compilers_by_ext, getFlagsByCompiler(entry, compilers_by_ext))
    next_compilers = {compiler for compiler in compilers_by_ext.values()}

    entry["compile_profiles"] = compile_profiles
    entry["link_compiler"] = pick_linker_compiler(compilers_by_ext)
    entry["rel_sources"] = relative_sources_path
    entry["obj_expr"] = objs_from_sources(relative_sources_path)
    write_config_entries(config_path, entries)

    print(f"Updated {config_path}")
    print(f"Updated sources for entry {args.entry_index}")
    for src in relative_sources_path:
        print(f"  - {src}")

    return 1 if next_compilers - previous_compilers else 0


if __name__ == "__main__":
    sys.exit(setJsonSources())
