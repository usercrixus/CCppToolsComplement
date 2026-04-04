from __future__ import annotations

import argparse
from pathlib import Path

from Classes.SourceTextsByPath import getSourceTexts
from Classes.TraversalResult import getTraversalResult
from globals import SOURCE_EXTENSIONS
from text.printer import format_stringified_headers
from strigify.stringify import stringify_headers
from utils import normalize_excluded_paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("startPath")
    parser.add_argument("excludedFolderPath", nargs="*")
    args = parser.parse_args()
    startPath = args.startPath
    excludedFolderPath = args.excludedFolderPath
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = normalize_excluded_paths(excludedFolderPath)
    source_extensions = SOURCE_EXTENSIONS
    source_texts_by_path = getSourceTexts(start_path, excluded_paths, source_extensions)
    traversal_result = getTraversalResult(startPath, excludedFolderPath, source_texts_by_path).setRecurence()

    stringified_headers = stringify_headers(traversal_result.generated_headers)
    print(format_stringified_headers(stringified_headers))


if __name__ == "__main__":
    main()
