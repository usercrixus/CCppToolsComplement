from __future__ import annotations

import argparse
from pathlib import Path

from Classes.Header.Header import Header
from Classes.Header.HeaderTexts import getHeaderTexts, getIncludeSet
from Classes.Header.InlineSourceCleanup import move_header_implementations_to_sources
from Classes.Source.SourceTexts import getSourceTexts
from Classes.Symbol.Symbol import correctIncludeSet, getSymbolMap
from conditionalPathExpander import expand_texts_by_conditional_path
from globals import HEADER_EXTENSIONS, SOURCE_EXTENSIONS
from regexTools.getMains import get_mains_source_paths
from text.printer import format_stringified_headers
from text.stringify import stringify
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
    main_source_paths = get_mains_source_paths(start_path, excluded_paths, SOURCE_EXTENSIONS)
    source_texts_by_path = getSourceTexts(start_path, excluded_paths, SOURCE_EXTENSIONS)
    header_texts_by_path = getHeaderTexts(start_path, excluded_paths, HEADER_EXTENSIONS)
    source_texts_by_path = expand_texts_by_conditional_path(source_texts_by_path, main_source_paths)
    header_texts_by_path = expand_texts_by_conditional_path(header_texts_by_path)
    source_texts_by_path, header_texts_by_path = move_header_implementations_to_sources(source_texts_by_path, header_texts_by_path,)
    merged_texts_by_path = {**source_texts_by_path, **header_texts_by_path}
    include_set = getIncludeSet(merged_texts_by_path)
    symbols = getSymbolMap(source_texts_by_path, merged_texts_by_path)
    include_set = correctIncludeSet(symbols, include_set)
    stringified_headers = stringify(symbols)
    stringified_headers.append(Header.create_include_set_render_job(str(start_path / "remainingIncludes.h"), include_set))
    print(format_stringified_headers(stringified_headers))


if __name__ == "__main__":
    main()
