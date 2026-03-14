#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Callable

from srcs.script.utils import program_from_output_makefile

JsonObject = dict[str, Any]
FieldValidator = Callable[[int, JsonObject, Any], list[str]]
REQUIRED_ENTRY_FIELDS = {
    "output_makefile",
    "link_compiler",
    "link_flags",
    "run_args",
    "bin_name",
    "rel_sources",
    "obj_expr",
    "compile_profiles",
}


def tokenized_obj_expr(obj_expr: str) -> list[str]:
    return [part for part in obj_expr.split(" ") if part.strip()]


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_compile_profiles(entry_index: int, compile_profiles: Any) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    extensions: set[str] = set()
    if not isinstance(compile_profiles, list) or not compile_profiles:
        return [f"[entry {entry_index}] 'compile_profiles' must be a non-empty list."], extensions

    for profile_index, profile in enumerate(compile_profiles):
        if not isinstance(profile, dict):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} must be an object.")
            continue
        ext = profile.get("ext")
        compiler = profile.get("compiler")
        flags = profile.get("flags")
        if not is_non_empty_string(ext):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'ext'.")
        elif not str(ext).startswith("."):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} ext must start with '.'.")
        else:
            extensions.add(str(ext))
        if not is_non_empty_string(compiler):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'compiler'.")
        if not isinstance(flags, str):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'flags'.")

    return errors, extensions


def validate_compile_profile_extensions(entry_index: int, rel_sources: list[str], extensions: set[str]) -> list[str]:
    rel_exts = {Path(src).suffix for src in rel_sources if Path(src).suffix}
    missing = sorted(ext for ext in rel_exts if ext not in extensions)
    if not missing:
        return []
    return [f"[entry {entry_index}] Missing compile profile(s) for source extension(s): {', '.join(missing)}."]


def validate_output_makefile(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not is_non_empty_string(value):
        return [f"[entry {entry_index}] 'output_makefile' must be a non-empty string."]
    errors: list[str] = []
    output_path = Path(str(value))
    if not output_path.is_absolute():
        errors.append(f"[entry {entry_index}] 'output_makefile' should be an absolute path.")
    if not program_from_output_makefile(output_path):
        errors.append(f"[entry {entry_index}] output_makefile filename must match Makefile.<program>.")
    return errors


def validate_link_compiler(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not is_non_empty_string(value):
        return [f"[entry {entry_index}] 'link_compiler' must be a non-empty string."]
    return []


def validate_link_flags(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not isinstance(value, str):
        return [f"[entry {entry_index}] 'link_flags' must be a string."]
    return []


def validate_run_args(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not isinstance(value, str):
        return [f"[entry {entry_index}] 'run_args' must be a string."]
    return []


def validate_bin_name(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not is_non_empty_string(value):
        return [f"[entry {entry_index}] 'bin_name' must be a non-empty string."]
    return []


def validate_rel_sources(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"[entry {entry_index}] 'rel_sources' must be a non-empty list of strings."]

    errors: list[str] = []
    for source_index, source in enumerate(value):
        if not is_non_empty_string(source):
            errors.append(f"[entry {entry_index}] rel_sources[{source_index}] must be a non-empty string.")
            continue
        source_str = str(source)
        if Path(source_str).is_absolute():
            errors.append(f"[entry {entry_index}] rel_sources[{source_index}] must be relative.")
    return errors


def validate_obj_expr(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    if not is_non_empty_string(value):
        return [f"[entry {entry_index}] 'obj_expr' must be a non-empty string."]

    obj_tokens = tokenized_obj_expr(str(value))
    if not obj_tokens:
        return [f"[entry {entry_index}] 'obj_expr' cannot be blank."]

    errors: list[str] = []
    for token_index, token in enumerate(obj_tokens):
        if Path(token).suffix != ".o":
            errors.append(f"[entry {entry_index}] obj_expr token #{token_index} ('{token}') must end with .o.")
    errors.extend(getSrcsObjsMatch(entry_index, extract_rel_sources(entry.get("rel_sources")), obj_tokens))
    return errors


def validate_compile_profiles_field(entry_index: int, entry: JsonObject, value: Any) -> list[str]:
    profile_errors, extensions = validate_compile_profiles(entry_index, value)
    profile_errors.extend(
        validate_compile_profile_extensions(entry_index, extract_rel_sources(entry.get("rel_sources")), extensions)
    )
    return profile_errors


def extract_rel_sources(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    rel_sources: list[str] = []
    for source in value:
        if not is_non_empty_string(source):
            continue
        source_str = str(source)
        if Path(source_str).is_absolute():
            continue
        rel_sources.append(source_str)
    return rel_sources


def getFieldValidator(key: str):
    field_validators: dict[str, FieldValidator] = {
        "output_makefile": validate_output_makefile,
        "link_compiler": validate_link_compiler,
        "link_flags": validate_link_flags,
        "run_args": validate_run_args,
        "bin_name": validate_bin_name,
        "rel_sources": validate_rel_sources,
        "obj_expr": validate_obj_expr,
        "compile_profiles": validate_compile_profiles_field,
    }
    return field_validators[key]


def getFieldErrors(entry_index: int, entry: JsonObject):
    errors: list[str] = []
    for field_key, field_value in entry.items():
        validator = getFieldValidator(field_key)
        if validator is None:
            errors.append(f"[entry {entry_index}] Unsupported field '{field_key}'.")
        else:
            errors.extend(validator(entry_index, entry, field_value))
    return errors


def getSrcsObjsMatch(entry_index: int, rel_sources, obj_tokens):
    errors: list[str] = []
    if (
        isinstance(rel_sources, list)
        and isinstance(obj_tokens, list)
        and rel_sources
        and obj_tokens
        and len(rel_sources) != len(obj_tokens)
    ):
        errors.append(
            f"[entry {entry_index}] rel_sources count ({len(rel_sources)}) "
            f"does not match obj_expr token count ({len(obj_tokens)})."
        )
    return errors


def getMissingFieldErrors(entry_index: int, entry: JsonObject):
    errors: list[str] = []
    for missing_field in sorted(REQUIRED_ENTRY_FIELDS - set(entry.keys())):
        errors.append(f"[entry {entry_index}] Missing required field '{missing_field}'.")
    return errors


def getErrors(entry_index: int, entry: JsonObject) -> list[str]:
    errors: list[str] = []
    errors.extend(getFieldErrors(entry_index, entry))
    errors.extend(getMissingFieldErrors(entry_index, entry))
    return errors


def find_duplicate_output_makefiles(entries: list[JsonObject]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, int] = {}
    for index, entry in enumerate(entries):
        output_makefile = entry.get("output_makefile")
        if output_makefile in seen:
            first = seen[output_makefile]
            errors.append(
                f"[entry {index}] duplicate output_makefile '{output_makefile}' (already used by entry {first})."
            )
        else:
            seen[output_makefile] = index
    return errors


def load_entries_for_verify(config_path: Path) -> tuple[list[JsonObject], list[str]]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"Invalid JSON in {config_path}: {exc}"]
    except OSError as exc:
        return [], [f"Unable to read JSON file {config_path}: {exc}"]
    if not isinstance(data, list):
        return [], [f"JSON root must be an array: {config_path}"]
    entries = [item for item in data if isinstance(item, dict)]
    if not entries:
        return [], [f"No program entries found in {config_path}"]
    return entries, []


def printSummary(errors: list[str], config_path: Path, entries: list[JsonObject]):
    if errors:
        print(f"Verification failed for {config_path}:")
        for err in errors:
            print(f"- {err}")
    else:
        print(f"Verification passed for {config_path} ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}).")


def verifyjson() -> int:
    config_path = Path(".vscode/makefileConfig.json").resolve()
    entries, errors = load_entries_for_verify(config_path)
    for index, entry in enumerate(entries):
        errors.extend(getErrors(index, entry))
    errors.extend(find_duplicate_output_makefiles(entries))
    printSummary(errors, config_path, entries)
    return errors and 1 or 0


if __name__ == "__main__":
    raise SystemExit(verifyjson())
