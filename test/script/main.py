#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable

C_PROGRAM_DIR = ROOT / "test" / "cProgram"
MAIN_REL = "test/cProgram/main.c"
PROGRAM_NAME = "testCProgram"
BIN_NAME = f"{PROGRAM_NAME}.out"
OUTPUT_MAKEFILE_REL = f"test/cProgram/Makefile.{PROGRAM_NAME}"
HEADER_PATH = C_PROGRAM_DIR / "subfolder" / "header.h"

SCRIPT_GENERATE_JSON = ROOT / "srcs" / "script" / "generateJsonForMakefile.py"
SCRIPT_VERIFY_CONFIG = ROOT / "srcs" / "script" / "verifyMakefileConfig.py"
SCRIPT_GENERATE_MAKEFILE = ROOT / "srcs" / "script" / "generateMakefileFromJson.py"

DEFAULT_FLAGS = "-Wall -Wextra -Werror -MMD -MP"


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> str:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(
            completed.returncode, cmd, output=completed.stdout, stderr=completed.stderr
        )
    return completed.stdout


def reset_artifacts() -> None:
    vscode_dir = ROOT / ".vscode"
    if vscode_dir.exists():
        shutil.rmtree(vscode_dir)

    patterns = ["*.o", "*.d", "*.out", "Makefile", "Makefile.*"]
    for pattern in patterns:
        for path in C_PROGRAM_DIR.rglob(pattern):
            if path.is_file():
                path.unlink()


def set_define_test(value: str) -> None:
    lines = HEADER_PATH.read_text(encoding="utf-8").splitlines()
    updated = False
    for idx, line in enumerate(lines):
        if line.strip().startswith("#define DEFINE_TEST"):
            lines[idx] = f'#define DEFINE_TEST "{value}"'
            updated = True
            break
    if not updated:
        raise RuntimeError("Could not find '#define DEFINE_TEST' in header.")
    HEADER_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_all() -> None:
    generator_input = "\n".join(
        [
            MAIN_REL,
            PROGRAM_NAME,
            "",
            BIN_NAME,
            OUTPUT_MAKEFILE_REL,
            DEFAULT_FLAGS,
            "",
        ]
    )
    run([PYTHON, str(SCRIPT_GENERATE_JSON)], cwd=ROOT, input_text=generator_input)
    run([PYTHON, str(SCRIPT_VERIFY_CONFIG)], cwd=ROOT)
    run([PYTHON, str(SCRIPT_GENERATE_MAKEFILE)], cwd=ROOT)


def run_program() -> str:
    child_makefile = C_PROGRAM_DIR / f"Makefile.{PROGRAM_NAME}"
    run(
        ["make", "-f", str(child_makefile.name), "all"],
        cwd=C_PROGRAM_DIR,
        env_overrides={"CCACHE_DISABLE": "1"},
    )
    return run([str(C_PROGRAM_DIR / BIN_NAME)], cwd=C_PROGRAM_DIR)


def assert_output(actual: str, expected: str, step: str) -> None:
    normalized_actual = actual.strip()
    normalized_expected = expected.strip()
    if normalized_actual != normalized_expected:
        raise AssertionError(
            f"{step} output mismatch.\nExpected:\n{normalized_expected}\n\nActual:\n{normalized_actual}"
        )
    print(f"{step} output verified.")


def main() -> None:
    print("Resetting generated artifacts...")
    reset_artifacts()

    print('Setting header to baseline: #define DEFINE_TEST "define test"...')
    set_define_test("define test")

    print("Generating config + Makefiles (first pass)...")
    generate_all()

    print("Launching C program (first pass)...")
    output_first = run_program()
    assert_output(output_first, "define test\none\ntwo", "First pass")

    print('Updating header define to: #define DEFINE_TEST "define test update"...')
    set_define_test("define test update")

    print("Generating config + Makefiles (second pass)...")
    generate_all()

    print("Launching C program (second pass)...")
    output_second = run_program()
    assert_output(output_second, "define test update\none\ntwo", "Second pass")

    print("All checks passed. You can now launch a debugging session in VSCode.")


if __name__ == "__main__":
    main()
