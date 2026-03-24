#!/usr/bin/env python3
from pathlib import Path

from srcs.script.action.helper.utils import (
    compiler_var_key,
    getProgramNameFromMakefileName,
    read_entries,
)
from srcs.script.action.jsonMakefileConfig.verify import verifyJson

FORCED_DEBUG_FLAGS = ("-g3", "-O0")


def force_flags(flags: str, required_flags: tuple[str, ...] = FORCED_DEBUG_FLAGS) -> str:
    tokens = flags.split()
    for required_flag in required_flags:
        if required_flag not in tokens:
            tokens.append(required_flag)
    return " ".join(tokens)


def getUniqueCompiler(compile_profiles: list[dict]):
    unique_compilers: list[str] = []
    #divide here
    for profile in compile_profiles:
        compiler = profile["compiler"]
        if compiler not in unique_compilers:
            unique_compilers.append(compiler)
    return unique_compilers


def getCompilersVar(unique_compilers, var_key_by_compiler, compile_profiles):
    var_lines = []
    for compiler in unique_compilers:
        key = var_key_by_compiler[compiler]
        flags = next(profile["flags"] for profile in compile_profiles if profile["compiler"] == compiler)
        var_lines.append(f"COMPILER_{key} = {compiler}")
        var_lines.append(f"FLAGS_{key} = {force_flags(flags)}")
    return var_lines


def getPatternRules(compile_profiles, var_key_by_compiler):
    pattern_rules = []
    for profile in compile_profiles:
        ext = profile["ext"]
        compiler = profile["compiler"]
        key = var_key_by_compiler[compiler]
        pattern_rules.append(f"%.o: %{ext}\n\t$(COMPILER_{key}) $(FLAGS_{key}) -c $< -o $@\n")
    return pattern_rules


def render_child_makefile(
    compile_profiles: list[dict],
    link_compiler: str,
    link_flags: str,
    run_args: str,
    bin_name: str,
    rel_sources: list[str],
    obj_expr: str,
):
    srcs = " ".join(rel_sources)
    unique_compilers: list[str] = getUniqueCompiler(compile_profiles)
    var_key_by_compiler = {compiler: compiler_var_key(compiler) for compiler in unique_compilers}
    var_lines = getCompilersVar(unique_compilers, var_key_by_compiler, compile_profiles)
    link_key = var_key_by_compiler[link_compiler]
    pattern_rules = getPatternRules(compile_profiles, var_key_by_compiler)
    lines = [
        *var_lines,
        f"LINK_COMPILER = $(COMPILER_{link_key})",
        f"LINK_FLAGS = {force_flags(link_flags)}",
        f"ARGS = {run_args}",
        f"BIN = {bin_name}",
        f"SRCS = {srcs}",
        f"OBJS = {obj_expr}",
        "DEPS = $(OBJS:.o=.d)",
        "",
        "all: $(BIN)",
        "",
        "$(BIN): $(OBJS)",
        "\t$(LINK_COMPILER) $(LINK_FLAGS) $^ -o $@",
        "",
    ]
    lines.extend(pattern_rules)
    lines.extend(
        [
            "run: $(BIN)",
            "\t./$(BIN) $(ARGS)",
            "",
            "clean:",
            "\trm -f $(OBJS) $(DEPS)",
            "",
            "fclean: clean",
            "\trm -f $(BIN)",
            "",
            "re: fclean all",
            "",
            ".PHONY: all run clean fclean re",
            "",
            "-include $(DEPS)",
            "",
        ]
    )
    return "\n".join(lines)


def render_parent_makefile(programs: list[str]):
    run_rules = []
    build_rules = []
    all_rules = []
    clean_rules = []
    fclean_rules = []
    for prog in programs:
        run_rules.append(f"{prog}Run:\n\t$(MAKE) -f Makefile.{prog} run\n")
        build_rules.append(f"{prog}Build:\n\t$(MAKE) -f Makefile.{prog} all\n")
        all_rules.append(f"\t$(MAKE) -f Makefile.{prog} all")
        clean_rules.append(f"\t$(MAKE) -f Makefile.{prog} clean")
        fclean_rules.append(f"\t$(MAKE) -f Makefile.{prog} fclean")
    phony_program_rules = []
    for prog in programs:
        phony_program_rules.append(f"{prog}Build")
        phony_program_rules.append(f"{prog}Run")
    phony = " ".join(["all"] + phony_program_rules + ["clean", "fclean", "re"])
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


def require(entry: dict, key: str):
    if key not in entry:
        raise SystemExit(f"Missing key '{key}' in JSON entry.")
    return entry[key]


def normalize_profiles(entry: dict) -> tuple[list[dict], str, str]:
    compile_profiles = require(entry, "compile_profiles")
    link_compiler = require(entry, "link_compiler")
    link_flags = require(entry, "link_flags")
    normalized = []
    for profile in compile_profiles:
        ext = profile.get("ext")
        compiler = profile.get("compiler")
        flags = profile.get("flags")
        normalized.append({"ext": ext, "compiler": compiler, "flags": flags})
    return normalized, link_compiler, link_flags


def generate_one(entry: dict) -> tuple[Path, str]:
    out_path = (Path.cwd() / str(require(entry, "output_makefile"))).resolve()
    run_args = require(entry, "run_args")
    bin_name = require(entry, "bin_name")
    rel_sources = require(entry, "rel_sources")
    obj_expr = require(entry, "obj_expr")
    compile_profiles, link_compiler, link_flags = normalize_profiles(entry)
    makefile_text = render_child_makefile(
        compile_profiles,
        link_compiler,
        link_flags,
        str(run_args),
        str(bin_name),
        rel_sources,
        str(obj_expr),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(makefile_text, encoding="utf-8")
    program = getProgramNameFromMakefileName(out_path)
    return out_path, program


def generateChildMakefiles(entries: list[dict]) -> dict[Path, set[str]]:
    programs_by_dir: dict[Path, set[str]] = {}
    for entry in entries:
        out_path, program = generate_one(entry)
        programs_by_dir.setdefault(out_path.parent, set()).add(program)
        print(f"Generated {out_path}")
    return programs_by_dir


def generatedParentMakefiles(programs_by_dir: dict[Path, set[str]]):
    for directory in sorted(programs_by_dir):
        programs = sorted(programs_by_dir[directory])
        parent_path = directory / "Makefile"
        parent_path.write_text(render_parent_makefile(programs), encoding="utf-8")
        print(f"Updated parent {parent_path}")
        print("Parent rules:")
        for prog in programs:
            print(f"  - {prog}")


def generateMakefile() -> None:
    if verifyJson() != 0:
        raise SystemExit("Makefile configuration verification failed.")
    config_path = Path(".vscode/makefileConfig.json").resolve()
    entries = read_entries(config_path)
    programs_by_dir = generateChildMakefiles(entries)
    generatedParentMakefiles(programs_by_dir)


if __name__ == "__main__":
    generateMakefile()
