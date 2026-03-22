#!/usr/bin/env python3
import argparse
import re
import os
import json
from pathlib import Path
from typing import Optional

from srcs.script.utils import getCompiler

SRC_EXTS = [".cpp", ".cc", ".cxx", ".c"]
HDR_EXTS = [".hpp", ".hh", ".hxx", ".h"]
INCLUDE_RE = re.compile(r'^\s*#\s*include\s*"([^"]+)"')
CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_local_includes(path: Path):
    includes = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    for line in text.splitlines():
        m = INCLUDE_RE.match(line)
        if m:
            includes.append(m.group(1))
    return includes


def resolve_include(include_name: str, base_file: Path, project_root: Path):
    candidates = [
        (base_file.parent / include_name),
        (project_root / include_name),
    ]
    for cand in candidates:
        if cand.exists():
            return cand.resolve()
    return None


def sibling_source_for(header_path: Path, preferred_ext: str):
    stem = header_path.with_suffix("")
    preferred = stem.with_suffix(preferred_ext)
    if preferred.exists():
        return preferred.resolve()
    for ext in SRC_EXTS:
        cand = stem.with_suffix(ext)
        if cand.exists():
            return cand.resolve()
    return None


def discover_sources(main_src: Path, project_root: Path):
    preferred_ext = main_src.suffix
    queue = [main_src.resolve()]
    seen = set()
    sources = set()

    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)

        if current.suffix in SRC_EXTS:
            sources.add(current)

        for include_name in parse_local_includes(current):
            included = resolve_include(include_name, current, project_root)
            if included is None:
                continue
            if included not in seen:
                queue.append(included)
            if included.suffix in HDR_EXTS:
                sibling = sibling_source_for(included, preferred_ext)
                if sibling and sibling not in seen:
                    queue.append(sibling)

    main_resolved = main_src.resolve()
    return sorted(sources, key=lambda p: (0 if p == main_resolved else 1, str(p)))


def objs_from_sources(rel_sources: list[str]):
    objs = []
    for src in rel_sources:
        if "." in src:
            objs.append(src.rsplit(".", 1)[0] + ".o")
        else:
            objs.append(src + ".o")
    return " ".join(objs)


def program_from_submake(path: Path) -> Optional[str]:
    name = path.name
    prefix = "Makefile."
    if not name.startswith(prefix):
        return None
    prog = name[len(prefix) :].strip()
    if prog.endswith(".json"):
        return None
    return prog or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update one entry in .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "--main-path",
        required=True,
        help="Path to the main source file.",
    )
    parser.add_argument(
        "--program-name",
        required=True,
        help="Program name. Must match Makefile.<program>.",
    )
    parser.add_argument(
        "--run-args",
        default="",
        help="Run arguments string.",
    )
    parser.add_argument(
        "--bin-name",
        default="",
        help="Binary name. Defaults to <program>.out.",
    )
    parser.add_argument(
        "--output-path",
        default="",
        help="Output Makefile path. Defaults to <main-dir>/Makefile.<program>.",
    )
    return parser.parse_args()


def getMainPath(main_input: str, project_root: Path) -> Path:
    main_path = Path(main_input)
    if not main_path.is_absolute():
        main_path = (project_root / main_path).resolve()
    if not main_path.exists():
        raise SystemExit(f"Main file not found: {main_path}")
    if main_path.suffix not in SRC_EXTS:
        raise SystemExit(
            f"Unsupported main extension '{main_path.suffix}'. Supported: {', '.join(SRC_EXTS)}"
        )
    return main_path


def getSource(main_path: Path, project_root: Path) -> list[Path]:
    sources = discover_sources(main_path, project_root)
    if not sources:
        sources = [main_path.resolve()]
    return sources


def getOutputPath(output_input: str, project_root: Path, main_path: Path, program_name: str) -> Path:
    if output_input:
        out_path = Path(output_input)
        if not out_path.is_absolute():
            out_path = (project_root / out_path).resolve()
    else:
        out_path = (main_path.parent / f"Makefile.{program_name}").resolve()

    if out_path.name == "Makefile":
        raise SystemExit("Output path must be a sub-Makefile, not the parent Makefile.")
    if not out_path.name.startswith("Makefile."):
        raise SystemExit("Output filename must match format: Makefile.<program>")
    path_program = program_from_submake(out_path)
    if path_program != program_name:
        raise SystemExit(
            f"Program name '{program_name}' must match output filename suffix '{path_program}'."
        )
    return out_path


def getRelativePath(sources: list[Path], start: Path):
    return [os.path.relpath(src.resolve(), start.resolve()).replace("\\", "/") for src in sources]


def detect_compilers_by_ext(relative_sources_path: list[str]) -> dict[str, str]:
    compilers_by_ext: dict[str, str] = {}
    for src in relative_sources_path:
        ext = Path(src).suffix
        if not ext:
            continue
        if ext in compilers_by_ext:
            continue
        compilers_by_ext[ext] = getCompiler(ext)
    return compilers_by_ext


def build_compile_profiles(compilers_by_ext: dict[str, str], flags_by_compiler: dict[str, str]) -> list[dict]:
    profiles = []
    for ext in sorted(compilers_by_ext.keys()):
        compiler = compilers_by_ext[ext]
        profiles.append(
            {
                "ext": ext,
                "compiler": compiler,
                "flags": flags_by_compiler[compiler],
            }
        )
    return profiles


def pick_linker_compiler(compilers_by_ext: dict[str, str]) -> str:
    compilers = set(compilers_by_ext.values())
    if "g++" in compilers:
        return "g++"
    if "gcc" in compilers:
        return "gcc"
    raise SystemExit("No supported compiler detected from source files.")


def read_config_entries(config_path: Path) -> list[dict]:
    if not config_path.exists():
        return []
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(data, list):
        raise SystemExit(f"{config_path} must contain a JSON array.")
    entries: list[dict] = []
    for item in data:
        if isinstance(item, dict):
            entries.append(item)
    return entries


def upsert_config_entry(entries: list[dict], payload: dict) -> list[dict]:
    out_path = payload["output_makefile"]
    replaced = False
    result = []
    for entry in entries:
        if entry.get("output_makefile") == out_path:
            result.append(payload)
            replaced = True
        else:
            result.append(entry)
    if not replaced:
        result.append(payload)
    return result


def write_config_entries(config_path: Path, entries: list[dict]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def generateJson() -> None:
    project_root = Path.cwd()
    args = parse_args()
    main_input = args.main_path
    program_name = args.program_name
    args_input = args.run_args
    bin_input = args.bin_name
    output_input = args.output_path

    main_path = getMainPath(main_input, project_root)
    sources = getSource(main_path, project_root)
    out_path = getOutputPath(output_input, project_root, main_path, program_name)
    relative_sources_path = getRelativePath(sources, out_path.parent)
    obj_expr = objs_from_sources(relative_sources_path)
    compilers_by_ext = detect_compilers_by_ext(relative_sources_path)
    flags_by_compiler = {compiler: "" for compiler in sorted(set(compilers_by_ext.values()))}
    compile_profiles = build_compile_profiles(compilers_by_ext, flags_by_compiler)
    link_compiler = pick_linker_compiler(compilers_by_ext)
    link_flags = ""
    bin_name = bin_input if bin_input else f"{program_name}.out"
    config_path = (project_root / CONFIG_REL_PATH).resolve()

    payload = {
        "output_makefile": os.path.relpath(out_path, project_root).replace("\\", "/"),
        "parent_makefile": os.path.relpath(out_path.parent / "Makefile", project_root).replace("\\", "/"),
        "compile_profiles": compile_profiles,
        "link_compiler": link_compiler,
        "link_flags": link_flags,
        "run_args": args_input,
        "bin_name": bin_name,
        "rel_sources": relative_sources_path,
        "obj_expr": obj_expr,
    }
    current_entries = read_config_entries(config_path)
    next_entries = upsert_config_entry(current_entries, payload)
    write_config_entries(config_path, next_entries)

    print(f"Generated {config_path}")
    print("Detected SRCS:")
    for src in relative_sources_path:
        print(f"  - {src}")


if __name__ == "__main__":
    generateJson()
