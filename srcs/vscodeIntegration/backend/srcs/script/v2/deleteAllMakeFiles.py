#!/usr/bin/env python3
from pathlib import Path

from srcs.script.v2.utils import getProgramNameFromMakefileName, read_entries

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def getManagedMakefilePaths(workspace_root: Path, entries: list[dict]) -> set[Path]:
    makefile_paths: set[Path] = set()
    for entry in entries:
        output_makefile = entry.get("output_makefile")
        if not isinstance(output_makefile, str) or not output_makefile.strip():
            continue
        makefile_paths.add((workspace_root / output_makefile).resolve())

    for candidate in workspace_root.rglob("Makefile.*"):
        if not candidate.is_file():
            continue
        if getProgramNameFromMakefileName(candidate) is None:
            continue
        makefile_paths.add(candidate.resolve())
    return makefile_paths


def deleteAllMakeFiles() -> None:
    config_path = (Path.cwd() / CONFIG_REL_PATH).resolve()
    entries = read_entries(config_path) if config_path.exists() else []

    workspace_root = Path.cwd().resolve()
    deleted_count = 0
    parent_makefiles: set[Path] = set()
    makefile_paths = getManagedMakefilePaths(workspace_root, entries)

    for makefile_path in sorted(makefile_paths):
        parent_makefiles.add(makefile_path.parent / "Makefile")
        if not makefile_path.exists() or not makefile_path.is_file():
            continue

        makefile_path.unlink()
        deleted_count += 1
        print(f"Deleted {makefile_path}")

    for parent_makefile_path in sorted(parent_makefiles):
        if not parent_makefile_path.exists() or not parent_makefile_path.is_file():
            continue
        parent_makefile_path.unlink()
        deleted_count += 1
        print(f"Deleted {parent_makefile_path}")

    print(f"Deleted {deleted_count} makefile(s).")


if __name__ == "__main__":
    deleteAllMakeFiles()
