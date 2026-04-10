from __future__ import annotations

from pathlib import Path

from regexTools.common import ELIF_DEFINED_RE, ELSE_RE, ENDIF_RE, IFDEF_RE, IFNDEF_RE

Condition = tuple[str, bool]
ConditionSet = tuple[Condition, ...]


def _condition_suffix(conditions: ConditionSet) -> str:
    sorted_conditions = sorted(conditions, key=lambda condition: condition[0])
    return "".join(
        f"{'d' if is_positive else 'n'}{symbol}"
        for symbol, is_positive in sorted_conditions
    )


def expand_text_to_full_conditional_variants(
    file_path: Path,
    file_text: str,
) -> dict[str, str]:
    condition_stack: list[Condition] = []
    lines_with_conditions: list[tuple[ConditionSet, str]] = []
    variant_condition_sets: set[ConditionSet] = set()

    for line in file_text.splitlines(keepends=True):
        ifdef_match = IFDEF_RE.match(line)
        if ifdef_match:
            condition_stack.append((ifdef_match.group(1), True))
            continue

        ifndef_match = IFNDEF_RE.match(line)
        if ifndef_match:
            condition_stack.append((ifndef_match.group(1), False))
            continue

        elif_defined_match = ELIF_DEFINED_RE.match(line)
        if elif_defined_match and condition_stack:
            symbol = elif_defined_match.group(2) or elif_defined_match.group(3)
            is_negated = bool(elif_defined_match.group(1))
            condition_stack[-1] = (symbol, not is_negated)
            continue

        if ELSE_RE.match(line) and condition_stack:
            symbol, is_positive = condition_stack[-1]
            condition_stack[-1] = (symbol, not is_positive)
            continue

        if ENDIF_RE.match(line):
            if condition_stack:
                condition_stack.pop()
            continue

        conditions = tuple(condition_stack)
        lines_with_conditions.append((conditions, line))
        if conditions:
            variant_condition_sets.add(conditions)

    resolved_file_path = file_path.expanduser().resolve()
    rendered_variants: dict[str, str] = {}

    for variant_conditions in sorted(variant_condition_sets):
        variant_condition_lookup = set(variant_conditions)
        variant_lines = [
            line
            for line_conditions, line in lines_with_conditions
            if not line_conditions or set(line_conditions).issubset(variant_condition_lookup)
        ]
        if not variant_lines:
            continue

        variant_path = resolved_file_path.with_name(
            f"{resolved_file_path.stem}_full_conditional_{_condition_suffix(variant_conditions)}{resolved_file_path.suffix}"
        )
        rendered_variants[str(variant_path)] = "".join(variant_lines)

    return rendered_variants


def expand_texts_to_full_conditional_variants(
    texts_by_path: dict[str, str],
    target_file_paths: set[Path] | None = None,
) -> dict[str, str]:
    normalized_target_file_paths = {
        target_file_path.expanduser().resolve()
        for target_file_path in (target_file_paths or set())
    }
    expanded_texts_by_path: dict[str, str] = {}

    for file_path, file_text in texts_by_path.items():
        resolved_file_path = Path(file_path).expanduser().resolve()
        if normalized_target_file_paths and resolved_file_path not in normalized_target_file_paths:
            expanded_texts_by_path[str(resolved_file_path)] = file_text
            continue

        expanded_texts_by_path.update(
            expand_text_to_full_conditional_variants(resolved_file_path, file_text)
        )

    return expanded_texts_by_path


def build_main_variant_files(
    source_texts_by_path: dict[str, str],
    main_source_paths: set[Path],
) -> list[dict[str, str]]:
    main_variant_texts_by_path = expand_texts_to_full_conditional_variants(
        source_texts_by_path,
        main_source_paths,
    )
    normalized_main_source_paths = {
        main_source_path.expanduser().resolve()
        for main_source_path in main_source_paths
    }
    return [
        {"path": file_path, "string": file_text}
        for file_path, file_text in sorted(main_variant_texts_by_path.items())
        if Path(file_path).expanduser().resolve() not in normalized_main_source_paths
    ]
