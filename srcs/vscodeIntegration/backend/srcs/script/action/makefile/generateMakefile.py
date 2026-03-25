#!/usr/bin/env python3
import argparse
from pathlib import Path

from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.MakefileConfigEntry.utils import readEntries
from srcs.script.action.jsonMakefileConfig.verify import verifyJson
from srcs.script.action.makefile.Makefile import Makefile

CONFIG_REL_PATH = Path(".vscode/makefileConfig.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one makefile from .vscode/makefileConfig.json.",
    )
    parser.add_argument(
        "entry_index",
        type=int,
        help="Generate the makefile for the entry at this index.",
    )
    return parser.parse_args()


def getEntryByIndex(entries: list[MakefileConfigEntry], entry_index: int) -> MakefileConfigEntry:
    if not entries:
        raise ValueError("No program entries found in .vscode/makefileConfig.json")
    if entry_index < 0 or entry_index >= len(entries):
        raise ValueError(f"Entry index {entry_index} is out of range.")
    return entries[entry_index]


def renderParentMakefile(programs: list[str]) -> str:
    run_rules: list[str] = []
    build_rules: list[str] = []
    all_rules: list[str] = []
    clean_rules: list[str] = []
    fclean_rules: list[str] = []

    for program in programs:
        run_rules.append(f"{program}Run:\n\t$(MAKE) -f Makefile.{program} run\n")
        build_rules.append(f"{program}Build:\n\t$(MAKE) -f Makefile.{program} all\n")
        all_rules.append(f"\t$(MAKE) -f Makefile.{program} all")
        clean_rules.append(f"\t$(MAKE) -f Makefile.{program} clean")
        fclean_rules.append(f"\t$(MAKE) -f Makefile.{program} fclean")

    phony_program_rules: list[str] = []
    for program in programs:
        phony_program_rules.append(f"{program}Build")
        phony_program_rules.append(f"{program}Run")

    phony = " ".join(["all", *phony_program_rules, "clean", "fclean", "re"])
    return (
        "all:\n"
        + "\n".join(all_rules)
        + "\n\n"
        + "\n".join(build_rules)
        + "\n\n"
        + "\n".join(run_rules)
        + "\n"
        + "clean:\n"
        + "\n".join(clean_rules)
        + "\n\n"
        + "fclean:\n"
        + "\n".join(fclean_rules)
        + "\n\n"
        + "re: fclean all\n\n"
        + f".PHONY: {phony}\n"
    )


def getProgramsForDirectory(entries: list[MakefileConfigEntry], directory: Path, workspace_root: Path) -> list[str]:
    programs: set[str] = set()
    for entry in entries:
        output_makefile = (workspace_root / entry.output_makefile).resolve()
        if output_makefile.parent != directory:
            continue
        program = Makefile.getProgramNameFromMakefileName(output_makefile)
        if program is not None:
            programs.add(program)
    return sorted(programs)


def generateMakefile(entry_index: int) -> None:
    if verifyJson() != 0:
        raise SystemExit("Makefile configuration verification failed.")

    workspace_root = Path.cwd().resolve()
    config_path = (workspace_root / CONFIG_REL_PATH).resolve()
    entries = readEntries(config_path)
    entry = getEntryByIndex(entries, entry_index)
    makefile = Makefile(entry)
    output_makefile = makefile.outputMakefilePath(workspace_root)
    output_makefile.parent.mkdir(parents=True, exist_ok=True)
    output_makefile.write_text(makefile.generate(), encoding="utf-8")
    print(f"Generated {output_makefile}")

    programs = getProgramsForDirectory(entries, output_makefile.parent, workspace_root)
    parent_makefile = output_makefile.parent / "Makefile"
    parent_makefile.write_text(renderParentMakefile(programs), encoding="utf-8")
    print(f"Updated parent {parent_makefile}")


if __name__ == "__main__":
    generateMakefile(parse_args().entry_index)
