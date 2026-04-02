import argparse
from pathlib import Path
import os

from generateHeaderFromC import generateHeaderFromC
from generateHeaderFromCpp import generateHeaderFromCPP
from putAllHeaderInTmp import putAllHeaderInTmp


C_SOURCE_EXTENSIONS = {".c"}
CPP_SOURCE_EXTENSIONS = {".cc", ".cpp"}
# To avoid recursive include
# if limit = 1
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 1} put it in file/path1.c
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 0} put it in its own header
# more complexe if limit = 0
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path1.c", 2} put it in file/path1.c
# If # myMap["MY_MACRO"] = {"MY_MACRO 10", "file/path2.c", 1} put it in its own header
# If # myMap["MY_MACRO"] = {"MY_MACRO2 10", "file/path1.c", 2} put it in file/path1.c
# If # myMap["MY_MACRO"] = {"MY_MACRO2 10", "file/path2.c", 1} put it in its own header
# Put MY_MACRO MY_MACRO2 in the same header as the have the same shared folder using them

# Other possibilities :
#  Do a compiler that manage recursive include...
#  Let IA manage this part


# I suppose that 
RECURENCE_LIMIT = 0


def _normalize_excluded_paths(excluded_folder_paths):
    return {
        Path(folder_path).expanduser().resolve()
        for folder_path in excluded_folder_paths
    }


def _is_excluded(path, excluded_paths):
    return any(path == excluded_path or excluded_path in path.parents for excluded_path in excluded_paths)


def traverse_file_system(startPath, excludedFolderPath):
    start_path = Path(startPath).expanduser().resolve()
    excluded_paths = _normalize_excluded_paths(excludedFolderPath)

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

            if suffix in C_SOURCE_EXTENSIONS:
                generateHeaderFromC(str(file_path))
            elif suffix in CPP_SOURCE_EXTENSIONS:
                generateHeaderFromCPP(str(file_path))


# it get the path where it should start the traversing + a list of excluded folder
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("startPath")
    parser.add_argument("excludedFolderPath", nargs="*")
    args = parser.parse_args()

    startPath = args.startPath
    excludedFolderPath = args.excludedFolderPath
    traverse_file_system(startPath, excludedFolderPath)


if __name__ == "__main__":
    main()
