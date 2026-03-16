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
MODULE_GENERATE_JSON = "srcs.script.generateJson"
MODULE_GENERATE_MAKEFILE = "srcs.script.generateMakefileFromJson"
MODULE_GENERATE_VSCODE = "srcs.script.generateVscodeIntegrationFromJson"
PROGRAMS = [
    {
        "main_rel": "test/cProgram/main1.c",
        "program_name": "testCProgram1",
    },
    {
        "main_rel": "test/cProgram/main2.c",
        "program_name": "testCProgram2",
    },
]
HEADER_PATH = C_PROGRAM_DIR / "subfolder" / "header.h"
DEFAULT_FLAGS = "-Wall -Wextra -Werror -MMD -MP"
ANSI_GREEN = "\033[32m"
ANSI_ORANGE = "\033[38;5;208m"
ANSI_PINK = "\033[38;5;213m"
ANSI_RESET = "\033[0m"


def run(
    cmd: list[str],
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
    for program in PROGRAMS:
        main_rel = program["main_rel"]
        program_name = program["program_name"]
        bin_name = f"{program_name}.out"
        output_makefile_rel = f"test/cProgram/Makefile.{program_name}"
        generator_input = "\n".join(
            [
                main_rel,
                program_name,
                "",
                bin_name,
                output_makefile_rel,
                DEFAULT_FLAGS,
                DEFAULT_FLAGS,
                "",
            ]
        )
        run([PYTHON, "-m", MODULE_GENERATE_JSON], cwd=ROOT, input_text=generator_input)
    run([PYTHON, "-m", MODULE_GENERATE_MAKEFILE], cwd=ROOT)


def run_program(program_name: str) -> str:
    bin_name = f"{program_name}.out"
    child_makefile = C_PROGRAM_DIR / f"Makefile.{program_name}"
    run(
        ["make", "-f", str(child_makefile.name), "all"],
        cwd=C_PROGRAM_DIR,
        env_overrides={"CCACHE_DISABLE": "1"},
    )
    return run([str(C_PROGRAM_DIR / bin_name)], cwd=C_PROGRAM_DIR)


def assert_output(actual: str, expected: str, step: str) -> None:
    normalized_actual = actual.strip()
    normalized_expected = expected.strip()
    if normalized_actual != normalized_expected:
        raise AssertionError(
            f"{step} output mismatch.\nExpected:\n{normalized_expected}\n\nActual:\n{normalized_actual}"
        )
    print(f"{ANSI_GREEN}{step} output verified.{ANSI_RESET}")


def run_pass(define_value: str, expected_output: str, label: str) -> None:
    print(f"{ANSI_PINK}Run pass: {label}{ANSI_RESET}")
    print(f'Setting header define to: #define DEFINE_TEST "{define_value}"...')
    set_define_test(define_value)
    print(f"Generating config + Makefiles ({label})...")
    generate_all()
    print("")
    print(f"{ANSI_ORANGE}Launching C programs ({label})...{ANSI_RESET}")
    for program in PROGRAMS:
        print("")
        output = run_program(program["program_name"])
        assert_output(
            output,
            expected_output,
            f"{label.capitalize()} ({program['program_name']})",
        )


def main() -> None:
    print("Resetting generated artifacts...")
    reset_artifacts()
    print("")
    run_pass("define test", "define test\none\ntwo", "first pass")
    print("")
    run_pass("define test update", "define test update\none\ntwo", "second pass")
    print("")
    run([PYTHON, "-m", MODULE_GENERATE_VSCODE], cwd=ROOT)
    print(f"{ANSI_PINK}All checks passed. You can now launch a debugging session in VSCode.{ANSI_RESET}")


if __name__ == "__main__":
    main()
