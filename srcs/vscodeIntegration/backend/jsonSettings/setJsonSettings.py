#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from helper.utils import readJsonObject, writeJsonObject

SETTINGS_REL_PATH = Path(".vscode/settings.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set selected fields in .vscode/settings.json.",
    )
    parser.add_argument(
        "--file-exclude-exts",
        required=True,
        help='Space-separated extensions to exclude, for example ".o .c .cpp .txt".',
    )
    return parser.parse_args()


def parseExtensions(exts_text: str) -> list[str]:
    extensions: list[str] = []
    seen: set[str] = set()
    for raw_ext in exts_text.split():
        ext = raw_ext.strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        if ext in seen:
            continue
        seen.add(ext)
        extensions.append(ext)
    return extensions


def buildFilesExclude(extensions: list[str]) -> dict[str, bool]:
    return {f"**/*{ext}": True for ext in extensions}


def main() -> None:
    args = parse_args()
    settings_path = (Path.cwd() / SETTINGS_REL_PATH).resolve()
    settings = readJsonObject(settings_path, {})
    previous_files_exclude = settings.get("files.exclude", {})

    settings["files.exclude"] = buildFilesExclude(
        parseExtensions(args.file_exclude_exts)
    )
    writeJsonObject(settings_path, settings)

    print(f"Updated {settings_path}")
    print(
        "Updated files.exclude: "
        f"{json.dumps(previous_files_exclude, sort_keys=True)} -> "
        f"{json.dumps(settings['files.exclude'], sort_keys=True)}"
    )


if __name__ == "__main__":
    main()
