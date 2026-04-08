from __future__ import annotations

import argparse
from pathlib import Path

from Classes.Header import Header
from Classes.HeaderInlineSourceCleanup import move_header_implementations_to_sources
from Classes.HeaderTextsByPath import getHeaderTexts, getIncludeSet
from Classes.SourceTextsByPath import getSourceTexts
from Classes.TraversalResult import getTraversalResult
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
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
    header_extensions = HEADER_EXTENSIONS
    source_texts_by_path = getSourceTexts(start_path, excluded_paths, source_extensions)
    header_texts_by_path = getHeaderTexts(start_path, excluded_paths, header_extensions)
    source_texts_by_path, header_texts_by_path = move_header_implementations_to_sources(
        source_texts_by_path,
        header_texts_by_path,
    )
    merged_texts_by_path = {**source_texts_by_path, **header_texts_by_path}
    include_set = getIncludeSet(merged_texts_by_path)
    traversal_result = getTraversalResult(source_texts_by_path, merged_texts_by_path).setRecurence()
    include_set = traversal_result.correctIncludeSet(include_set)
    stringified_headers = stringify_headers(traversal_result.symbols)
    stringified_headers.append(
        Header.create_include_set_render_job(
            str(start_path / "remainingIncludes.h"),
            include_set,
        )
    )
    print(format_stringified_headers(stringified_headers))


if __name__ == "__main__":
    main()
