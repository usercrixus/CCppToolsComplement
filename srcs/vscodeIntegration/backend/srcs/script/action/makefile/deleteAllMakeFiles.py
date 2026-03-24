#!/usr/bin/env python3
from pathlib import Path

from srcs.script.action.helper.utils import getProgramNameFromMakefileName
from srcs.script.action.makefile.Makefile import Makefile
from srcs.script.action.makefile.utils import buildMakefiles, getOutputMakefilePath


def getManagedMakefilePaths(workspace_root: Path, makefiles: list[Makefile]) -> set[Path]:
    makefile_paths = {getOutputMakefilePath(makefile, workspace_root) for makefile in makefiles}

    for candidate in workspace_root.rglob("Makefile.*"):
        if not candidate.is_file():
            continue
        if getProgramNameFromMakefileName(candidate) is None:
            continue
        makefile_paths.add(candidate.resolve())

    return makefile_paths


def deleteAllMakeFiles() -> None:
    workspace_root = Path.cwd().resolve()
    makefiles = buildMakefiles()
    deleted_count = 0
    parent_makefiles: set[Path] = set()
    makefile_paths = getManagedMakefilePaths(workspace_root, makefiles)

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
