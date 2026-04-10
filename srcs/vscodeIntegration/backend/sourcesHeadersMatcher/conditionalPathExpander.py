from __future__ import annotations

from pathlib import Path

from regexTools.common import ELIF_DEFINED_RE, ELSE_RE, ENDIF_RE, IFDEF_RE, IFNDEF_RE


def expand_text_by_conditional_path(file_path: Path, file_text: str) -> dict[str, str]:
    condition_stack: list[tuple[str, bool]] = []
    texts_by_condition: dict[tuple[tuple[str, bool], ...], list[str]] = {(): []}

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

        current_condition = tuple(condition_stack)
        texts_by_condition.setdefault(current_condition, []).append(line)

    expanded_texts_by_path: dict[str, str] = {
        str(file_path.resolve()): "".join(texts_by_condition.get((), []))
    }

    for conditions, lines in texts_by_condition.items():
        if not conditions or not lines:
            continue

        sorted_conditions = sorted(conditions, key=lambda condition: condition[0])
        condition_suffix = "".join(
            f"{'d' if is_positive else 'n'}{symbol}"
            for symbol, is_positive in sorted_conditions
        )
        conditional_path = file_path.with_name(
            f"{file_path.stem}_conditional_{condition_suffix}{file_path.suffix}"
        ).resolve()
        expanded_texts_by_path[str(conditional_path)] = "".join(lines)

    return expanded_texts_by_path


def expand_texts_by_conditional_path(
    texts_by_path: dict[str, str],
    excluded_file_paths: set[Path] | None = None,
) -> dict[str, str]:
    normalized_excluded_file_paths = {
        excluded_file_path.expanduser().resolve()
        for excluded_file_path in (excluded_file_paths or set())
    }
    expanded_texts_by_path: dict[str, str] = {}

    for file_path, file_text in texts_by_path.items():
        resolved_file_path = Path(file_path).expanduser().resolve()
        if resolved_file_path in normalized_excluded_file_paths:
            expanded_texts_by_path[str(resolved_file_path)] = file_text
            continue

        expanded_texts_by_path.update(
            expand_text_by_conditional_path(resolved_file_path, file_text)
        )

    return expanded_texts_by_path
