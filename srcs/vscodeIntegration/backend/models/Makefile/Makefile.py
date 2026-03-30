from pathlib import Path
from typing import Any

from models.MakefileConfigEntry.CompileProfile import CompileProfile
from models.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from models.Exeption.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError

FORCED_DEBUG_FLAGS = ("-g3", "-O0", "-MMD", "-MP")


class Makefile:
    @staticmethod
    def getProgramNameFromMakefileName(output_makefile: Path) -> str | None:
        prefix = "Makefile."
        if not output_makefile.name.startswith(prefix):
            return None
        program = output_makefile.name[len(prefix) :].strip()
        if not program or "." in program:
            return None
        return program

    def __init__(self, makefile_config_entry: MakefileConfigEntry) -> None:
        self._output_makefile = makefile_config_entry.output_makefile
        self._compile_profiles: list[CompileProfile] = makefile_config_entry.compile_profiles
        self._link_compiler = makefile_config_entry.link_compiler
        self._link_flags = makefile_config_entry.link_flags
        self._args = makefile_config_entry.run_args
        self._bin = makefile_config_entry.bin_name
        self._srcs: list[str] = makefile_config_entry.rel_sources
        self._objs = makefile_config_entry.obj_expr
        self._deps = "$(OBJS:.o=.d)"
        self._pattern_rules: list[str] = []
        self.setPatternRules()

    def outputMakefilePath(self, workspace_root: Path | None = None) -> Path:
        if workspace_root is None:
            workspace_root = Path.cwd().resolve()
        return (workspace_root / self.output_makefile).resolve()

    @property
    def output_makefile(self) -> str:
        return self._output_makefile

    @property
    def compile_profiles(self) -> list[CompileProfile]:
        return self._compile_profiles

    @property
    def link_compiler(self) -> str:
        return self._link_compiler

    @property
    def link_flags(self) -> str:
        return self._link_flags

    @property
    def args(self) -> str:
        return self._args

    @property
    def bin(self) -> str:
        return self._bin

    @property
    def srcs(self) -> list[str]:
        return self._srcs

    @property
    def objs(self) -> str:
        return self._objs

    @property
    def deps(self) -> str:
        return self._deps

    @property
    def pattern_rules(self) -> list[str]:
        return self._pattern_rules

    def _forceFlags(self, flags: str, required_flags: tuple[str, ...] = FORCED_DEBUG_FLAGS) -> str:
        tokens = flags.split()
        for required_flag in required_flags:
            if required_flag not in tokens:
                tokens.append(required_flag)
        return " ".join(tokens)

    def setPatternRules(self) -> None:
        self._pattern_rules = [
            f"%.o: %{compile_profile.ext}\n"
            f"\t{compile_profile.compiler} {self._forceFlags(compile_profile.flags)} -c $< -o $@\n"
            for compile_profile in self.compile_profiles
        ]

    def generate(self) -> str:
        lines = [
            f"LINK_COMPILER = {self.link_compiler}",
            f"LINK_FLAGS = {self._forceFlags(self.link_flags)}",
            f"ARGS = {self.args}",
            f"BIN = {self.bin}",
            f"SRCS = {' '.join(self.srcs)}",
            f"OBJS = {self.objs}",
            f"DEPS = {self.deps}",
            "",
            "all: $(BIN)",
            "",
            "$(BIN): $(OBJS)",
            "\t$(LINK_COMPILER) $(LINK_FLAGS) $^ -o $@",
            "",
            *self.pattern_rules,
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
        return "\n".join(lines)
