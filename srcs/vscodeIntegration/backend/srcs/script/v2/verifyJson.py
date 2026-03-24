#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Callable

from srcs.script.v2.utils import getCompiler, getProgramNameFromMakefileName

JsonObject = dict[str, Any]
FieldErrorsByKey = dict[str, list[str]]
FieldValidator = Callable[[int, JsonObject, Any, FieldErrorsByKey], list[str]]
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


def getTokenizedObjExpr(obj_expr: str) -> list[str]:
    return [part for part in obj_expr.split(" ") if part.strip()]


def isNonEmptyString(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def getCompilerMatchErrors(entry_index: int, extension: str, compiler: str, context: str) -> list[str]:
    try:
        expected_compiler = getCompiler(extension)
    except ValueError:
        return [f"[entry {entry_index}] {context}: unsupported extension '{extension}'."]
    if compiler != expected_compiler:
        return [f"[entry {entry_index}] {context}: compiler '{compiler}' must match extension '{extension}' ({expected_compiler})."]
    return []


def getMissingExtensionErrors(entry_index: int, rel_sources: list[str], extensions: set[str]) -> list[str]:
    rel_exts = {Path(src).suffix for src in rel_sources if Path(src).suffix}
    missing = sorted(ext for ext in rel_exts if ext not in extensions)
    if not missing:
        return []
    return [f"[entry {entry_index}] Missing compile profile(s) for source extension(s): {', '.join(missing)}."]


def getExtensionFromCompileProfiles(entry_index: int, compile_profiles: Any) -> tuple[set[str], list[str]]:
    extensions: set[str] = set()
    errors = []
    if not isinstance(compile_profiles, list) or not compile_profiles:
        return extensions, [f"[entry {entry_index}] 'compile_profiles' must be a non-empty list."]
    for profile_index, profile in enumerate(compile_profiles):
        if not isinstance(profile, dict):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} must be an object.")
        else:
            ext = profile.get("ext")
            if not isNonEmptyString(ext):
                errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'ext'.")
            elif not str(ext).startswith("."):
                errors.append(f"[entry {entry_index}] compile profile #{profile_index} ext must start with '.'.")
            else:
                extensions.add(str(ext))
    return extensions, errors


def getCompileProfileCompilerErrors(entry_index: int, compile_profiles: Any) -> list[str]:
    errors = []
    if not isinstance(compile_profiles, list) or not compile_profiles:
        return [f"[entry {entry_index}] 'compile_profiles' must be a non-empty list."]
    for profile_index, profile in enumerate(compile_profiles):
        if not isinstance(profile, dict):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} must be an object.")
        else:
            ext = profile.get("ext")
            compiler = profile.get("compiler")
            if not isNonEmptyString(compiler):
                errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'compiler'.")
            elif isNonEmptyString(ext) and str(ext).startswith("."):
                errors.extend(
                    getCompilerMatchErrors(entry_index, str(ext), str(compiler), f"compile profile #{profile_index}")
                )
    return errors


def getCompileProfileFlagErrors(entry_index: int, compile_profiles: Any) -> list[str]:
    errors = []
    if not isinstance(compile_profiles, list) or not compile_profiles:
        return [f"[entry {entry_index}] 'compile_profiles' must be a non-empty list."]
    for profile_index, profile in enumerate(compile_profiles):
        if not isinstance(profile, dict):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} must be an object.")
        elif not isinstance(profile.get("flags"), str):
            errors.append(f"[entry {entry_index}] compile profile #{profile_index} has invalid 'flags'.")
    return errors


def getRelSources(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    rel_sources: list[str] = []
    for source in value:
        if not isNonEmptyString(source):
            continue
        source_str = str(source)
        if Path(source_str).is_absolute():
            continue
        rel_sources.append(source_str)
    return rel_sources


def getCompileProfilesErrors(
    entry_index: int,
    entry: JsonObject,
    value: Any,
    field_errors_by_key: FieldErrorsByKey,
) -> list[str]:
    errors: list[str] = []
    extensions, extension_errors = getExtensionFromCompileProfiles(entry_index, value)
    errors.extend(extension_errors)
    errors.extend(getCompileProfileCompilerErrors(entry_index, value))
    errors.extend(getCompileProfileFlagErrors(entry_index, value))
    if not field_errors_by_key.get("rel_sources"):
        errors.extend(getMissingExtensionErrors(entry_index, getRelSources(entry.get("rel_sources")), extensions))
    return errors


def getMakefileNameErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isNonEmptyString(value):
        return [f"[entry {entry_index}] 'output_makefile' must be a non-empty string."]
    errors: list[str] = []
    output_path = Path(str(value))
    if not getProgramNameFromMakefileName(output_path):
        errors.append(f"[entry {entry_index}] output_makefile filename must match Makefile.<program>.")
    return errors


def getLinkCompilerErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isNonEmptyString(value):
        return [f"[entry {entry_index}] 'link_compiler' must be a non-empty string."]
    if field_errors_by_key.get("rel_sources"):
        return []
    rel_sources = getRelSources(entry.get("rel_sources"))
    if not rel_sources:
        return [f"[entry {entry_index}] Cannot validate 'link_compiler': no valid main source found in 'rel_sources'."]
    main_extension = Path(rel_sources[0]).suffix
    if not main_extension:
        return [f"[entry {entry_index}] Cannot validate 'link_compiler': main source '{rel_sources[0]}' has no extension."]
    mismatch_errors = getCompilerMatchErrors(entry_index, main_extension, str(value), "link_compiler")
    if mismatch_errors:
        if "unsupported extension" in mismatch_errors[0]:
            return [f"[entry {entry_index}] Cannot validate 'link_compiler': unsupported main extension '{main_extension}'."]
        expected_compiler = getCompiler(main_extension)
        return [
            f"[entry {entry_index}] 'link_compiler' ({value}) must match the compiler for the main source "
            f"extension '{main_extension}' ({expected_compiler})."
        ]
    return []


def getLinkFlagErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isinstance(value, str):
        return [f"[entry {entry_index}] 'link_flags' must be a string."]
    return []


def getRunArgErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isinstance(value, str):
        return [f"[entry {entry_index}] 'run_args' must be a string."]
    return []


def getBinaryNameErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isNonEmptyString(value):
        return [f"[entry {entry_index}] 'bin_name' must be a non-empty string."]
    return []


def getRelSourceErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"[entry {entry_index}] 'rel_sources' must be a non-empty list of strings."]
    errors: list[str] = []
    for source_index, source in enumerate(value):
        if not isNonEmptyString(source):
            errors.append(f"[entry {entry_index}] rel_sources[{source_index}] must be a non-empty string.")
        elif Path(source).is_absolute():
            errors.append(f"[entry {entry_index}] rel_sources[{source_index}] must be relative.")
    return errors


def getSrcsObjsMatch(entry_index: int, rel_sources: list[str], obj_tokens: list[str]) -> list[str]:
    errors: list[str] = []
    if rel_sources and obj_tokens and len(rel_sources) != len(obj_tokens):
        errors.append(
            f"[entry {entry_index}] rel_sources count ({len(rel_sources)}) "
            f"does not match obj_expr token count ({len(obj_tokens)})."
        )
    return errors


def getObjExprErrors(entry_index: int, entry: JsonObject, value: Any, field_errors_by_key: FieldErrorsByKey) -> list[str]:
    if not isNonEmptyString(value):
        return [f"[entry {entry_index}] 'obj_expr' must be a non-empty string."]
    obj_tokens = getTokenizedObjExpr(str(value))
    if not obj_tokens:
        return [f"[entry {entry_index}] 'obj_expr' cannot be blank."]
    errors: list[str] = []
    for token_index, token in enumerate(obj_tokens):
        if Path(token).suffix != ".o":
            errors.append(f"[entry {entry_index}] obj_expr token #{token_index} ('{token}') must end with .o.")
    if not field_errors_by_key.get("rel_sources"):
        errors.extend(getSrcsObjsMatch(entry_index, getRelSources(entry.get("rel_sources")), obj_tokens))
    return errors


FIELD_VALIDATORS: list[tuple[str, FieldValidator]] = [
    ("output_makefile", getMakefileNameErrors),
    ("link_flags", getLinkFlagErrors),
    ("run_args", getRunArgErrors),
    ("bin_name", getBinaryNameErrors),
    ("rel_sources", getRelSourceErrors),
    ("obj_expr", getObjExprErrors),
    ("compile_profiles", getCompileProfilesErrors),
    ("link_compiler", getLinkCompilerErrors),
]


def getFieldErrors(entry_index: int, entry: JsonObject) -> list[str]:
    errors: list[str] = []
    field_errors_by_key: FieldErrorsByKey = {}
    known_keys = {field_key for field_key, _ in FIELD_VALIDATORS}
    for field_key in entry:
        if field_key == "parent_makefile":
            continue
        if field_key not in known_keys:
            errors.append(f"[entry {entry_index}] Unsupported field '{field_key}'.")
    for field_key, validator in FIELD_VALIDATORS:
        if field_key in entry:
            field_errors = validator(entry_index, entry, entry[field_key], field_errors_by_key)
            field_errors_by_key[field_key] = field_errors
            errors.extend(field_errors)
    return errors


def getMissingFieldErrors(entry_index: int, entry: JsonObject) -> list[str]:
    errors: list[str] = []
    for missing_field in sorted(REQUIRED_ENTRY_FIELDS - set(entry.keys())):
        errors.append(f"[entry {entry_index}] Missing required field '{missing_field}'.")
    return errors


def getEntryErrors(entry_index: int, entry: JsonObject) -> list[str]:
    errors: list[str] = []
    errors.extend(getFieldErrors(entry_index, entry))
    errors.extend(getMissingFieldErrors(entry_index, entry))
    return errors


def getDuplicateOutputMakefileErrors(entries: list[JsonObject]) -> list[str]:
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


def getEntries(config_path: Path) -> tuple[list[JsonObject], list[str]]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"Invalid JSON in {config_path}: {exc}"]
    except OSError as exc:
        return [], [f"Unable to read JSON file {config_path}: {exc}"]
    if not isinstance(data, list):
        return [], [f"JSON root must be an array: {config_path}"]
    entries = [item for item in data if isinstance(item, dict)]
    return entries, []


def printSummary(errors: list[str], config_path: Path, entries: list[JsonObject]) -> None:
    if errors:
        print(f"Verification failed for {config_path}:")
        for err in errors:
            print(f"- {err}")
    else:
        print(f"Verification passed for {config_path} ({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}).")


def verifyjson() -> int:
    config_path = Path(".vscode/makefileConfig.json").resolve()
    entries, errors = getEntries(config_path)
    for index, entry in enumerate(entries):
        errors.extend(getEntryErrors(index, entry))
    errors.extend(getDuplicateOutputMakefileErrors(entries))
    printSummary(errors, config_path, entries)
    return errors and 1 or 0


if __name__ == "__main__":
    raise SystemExit(verifyjson())
