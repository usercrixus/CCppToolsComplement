#!/usr/bin/env python3
from pathlib import Path

from srcs.script.action.helper.utils import getProgramNameFromMakefileName
from srcs.script.action.jsonMakefileConfig.verify import verifyJson
from srcs.script.action.makefile.Makefile import Makefile
from srcs.script.action.makefile.utils import buildMakefiles, getOutputMakefilePath


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
def generateChildMakefiles(makefiles: list[Makefile]) -> dict[Path, set[str]]:
    programs_by_dir: dict[Path, set[str]] = {}

    for makefile in makefiles:
        output_makefile = getOutputMakefilePath(makefile)
        output_makefile.parent.mkdir(parents=True, exist_ok=True)
        output_makefile.write_text(makefile.generate(), encoding="utf-8")

        program = getProgramNameFromMakefileName(output_makefile)
        if program is not None:
            programs_by_dir.setdefault(output_makefile.parent, set()).add(program)

        print(f"Generated {output_makefile}")

    return programs_by_dir


def generateParentMakefiles(programs_by_dir: dict[Path, set[str]]) -> None:
    for directory in sorted(programs_by_dir):
        programs = sorted(programs_by_dir[directory])
        parent_makefile = directory / "Makefile"
        parent_makefile.write_text(renderParentMakefile(programs), encoding="utf-8")
        print(f"Updated parent {parent_makefile}")


def generateMakefile() -> None:
    if verifyJson() != 0:
        raise SystemExit("Makefile configuration verification failed.")

    makefiles = buildMakefiles()
    programs_by_dir = generateChildMakefiles(makefiles)
    generateParentMakefiles(programs_by_dir)


if __name__ == "__main__":
    generateMakefile()
