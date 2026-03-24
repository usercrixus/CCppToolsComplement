from typing import Any

from srcs.script.MakefileConfigEntry.CompileProfile import CompileProfile
from srcs.script.MakefileConfigEntry.MakefileConfigEntry import MakefileConfigEntry
from srcs.script.exception.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError


class Makefile:
    def __init__(self, makefile_config_entry: MakefileConfigEntry) -> None:
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

    def setPatternRules(self) -> None:
        self._pattern_rules = [
            f"%.o: %{compile_profile.ext}\n"
            f"\t{compile_profile.compiler} {compile_profile.flags} -c $< -o $@\n"
            for compile_profile in self.compile_profiles
        ]
