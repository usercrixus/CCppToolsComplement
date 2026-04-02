from pathlib import Path
import shutil
import tempfile


HEADER_EXTENSIONS = {".h", ".hpp"}
TMP_HEADERS_ROOT_NAME = "CCppToolsComplementHeaderGarden"


def _resolve_scan_path(folder_path):
    return Path(folder_path or ".").expanduser().resolve()


def _build_tmp_folder(scan_path, tmp_root):
    safe_anchor = scan_path.anchor.replace(":", "").replace("/", "") or "root"
    relative_scan_path = scan_path.relative_to(scan_path.anchor)
    return Path(tmp_root) / TMP_HEADERS_ROOT_NAME / safe_anchor / relative_scan_path


def putAllHeaderInTmp(folder_path=".", tmp_root=None):
    """
    Copy every header from ``folder_path`` into a dedicated temp subfolder.

    Returns the created temp folder path as a string.
    """

    scan_path = _resolve_scan_path(folder_path)
    if not scan_path.is_dir():
        raise NotADirectoryError(f"Cannot collect headers from '{scan_path}'.")

    tmp_headers_folder = _build_tmp_folder(scan_path, tmp_root or tempfile.gettempdir())
    tmp_headers_folder.mkdir(parents=True, exist_ok=True)

    for entry in scan_path.iterdir():
        if not entry.is_file() or entry.suffix.lower() not in HEADER_EXTENSIONS:
            continue
        shutil.copy2(entry, tmp_headers_folder / entry.name)

    return str(tmp_headers_folder)
