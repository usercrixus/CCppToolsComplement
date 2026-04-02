import argparse
import os
from pathlib import Path

from generateHeader import generateHeader
from putAllHeaderInTmp import putAllHeaderInTmp
from render import renderHeaders
from resolveProto import resolveProto


C_SOURCE_EXTENSIONS = {".c"}
CPP_SOURCE_EXTENSIONS = {".cc", ".cpp"}
# To avoid recursive include
# if limit = 1
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 1} put it in file/path1.c
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 0} put it in its own header
# more complexe if limit = 0
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 2}
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path2.c", 1}
# If # myMap["MY_MACRO"] = {"MY_MACRO2 10", "file/path1.c", 2}
# If # myMap["MY_MACRO"] = {"MY_MACRO2 10", "file/path2.c", 1}
# Put MY_MACRO MY_MACRO2 in the same header as the have the same shared folder using them

# Other possibilities :
#  Do a compiler that manage recursive include...
#  Let IA manage this part
RECURENCE_LIMIT = 0


def _normalize_excluded_paths(excluded_folder_paths):
    return {
        Path(folder_path).expanduser().resolve()
        for folder_path in excluded_folder_paths
    }


def _is_excluded(path, excluded_paths):
    return any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded_paths)


def _merge_header_map(global_header_map, file_header_map):
    for proto_name, entries in file_header_map.items():
        global_header_map.setdefault(proto_name, []).extend(entries)


def _format_rendered_headers(rendered_headers):
    if not rendered_headers:
        return "No headers generated."

    lines = []
    for header_path in sorted(rendered_headers):
        lines.append(f"{header_path}:")
        for proto in rendered_headers[header_path]:
            lines.append(f"  - {proto}")
        lines.append("")

    return "\n".join(lines).rstrip()


def traverse_file_system(startPath, excludedFolderPath):
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath)
    source_extensions = C_SOURCE_EXTENSIONS | CPP_SOURCE_EXTENSIONS
    proto = resolveProto(startPath, source_extensions, excludedFolderPath)
    generated_headers = {}

    for current_root, dir_names, file_names in os.walk(start_path):
        current_path = Path(current_root).resolve()
        if _is_excluded(current_path, excluded_paths):
            dir_names[:] = []
            continue

        dir_names[:] = [
            dir_name
            for dir_name in dir_names
            if not _is_excluded(current_path / dir_name, excluded_paths)
        ]

        putAllHeaderInTmp(current_path)

        for file_name in file_names:
            file_path = current_path / file_name
            suffix = file_path.suffix.lower()

            if suffix in source_extensions:
                file_header_map = generateHeader(str(file_path), proto)
                _merge_header_map(generated_headers, file_header_map)

    return {
        "proto": proto,
        "generatedHeaders": generated_headers,
    }


# it get the path where it should start the traversing + a list of excluded folder
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("startPath")
    parser.add_argument("excludedFolderPath", nargs="*")
    args = parser.parse_args()

    startPath = args.startPath
    excludedFolderPath = args.excludedFolderPath
    traversal_result = traverse_file_system(startPath, excludedFolderPath)
    generated_headers = traversal_result["generatedHeaders"]
    rendered_headers = renderHeaders(generated_headers)
    print(_format_rendered_headers(rendered_headers))


if __name__ == "__main__":
    main()
