from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from srcs.script.MakefileConfigEntry.CompileProfile import CompileProfile
from srcs.script.exception.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError


@dataclass
class MakefileConfigEntry:
    output_makefile: str = ""
    compile_profiles: list[CompileProfile] = field(default_factory=list)
    link_compiler: str = ""
    link_flags: str = ""
    run_args: str = ""
    bin_name: str = ""
    rel_sources: list[str] = field(default_factory=list)
    obj_expr: str = ""

    def setOutputMakefile(self, output_makefile: str) -> None:
        self.output_makefile = output_makefile

    def setCompileProfiles(self, compile_profiles: list[CompileProfile]) -> None:
        self.compile_profiles = compile_profiles
        compilers = {profile.compiler for profile in self.compile_profiles if profile.compiler}
        if "g++" in compilers:
            self.setLinkCompiler("g++")
        elif "gcc" in compilers:
            self.setLinkCompiler("gcc")
        elif self.compile_profiles:
            self.setLinkCompiler(self.compile_profiles[0].compiler)
        else:
            self.setLinkCompiler("")

    def setLinkCompiler(self, link_compiler: str) -> None:
        self.link_compiler = link_compiler

    def setLinkFlags(self, link_flags: str) -> None:
        self.link_flags = link_flags

    def setRunArgs(self, run_args: str) -> None:
        self.run_args = run_args

    def setBinName(self, bin_name: str) -> None:
        self.bin_name = bin_name

    def setRelSources(self, rel_sources: list[str]) -> None:
        self.rel_sources = rel_sources
        self.setCompileProfiles(self._buildCompileProfilesFromRelSources())
        self.setObjExpr(self._buildObjExprFromRelSources())

    def setObjExpr(self, obj_expr: str) -> None:
        self.obj_expr = obj_expr

    def _getFlagsByCompiler(self) -> dict[str, str]:
        return {profile.compiler: profile.flags for profile in self.compile_profiles if profile.compiler}

    def _getCompilersByExt(self) -> dict[str, str]:
        compilers_by_ext: dict[str, str] = {}
        for source in self.rel_sources:
            ext = Path(source).suffix
            if not ext or ext in compilers_by_ext:
                continue
            compilers_by_ext[ext] = self._getCompiler(ext)
        return compilers_by_ext

    def _getCompiler(self, ext: str) -> str:
        if ext == ".c":
            return "gcc"
        if ext in {".cpp", ".cc", ".cxx"}:
            return "g++"
        raise ValueError(f"Unsupported main extension: {ext}")

    def _buildCompileProfilesFromRelSources(self) -> list[CompileProfile]:
        flags_by_compiler = self._getFlagsByCompiler()
        compilers_by_ext = self._getCompilersByExt()
        return [
            CompileProfile(
                ext=ext,
                compiler=compiler,
                flags=flags_by_compiler.get(compiler, ""),
            )
            for ext, compiler in compilers_by_ext.items()
        ]

    def _buildObjExprFromRelSources(self) -> str:
        obj_tokens: list[str] = []
        for source in self.rel_sources:
            if "." in source:
                obj_tokens.append(source.rsplit(".", 1)[0] + ".o")
            else:
                obj_tokens.append(source + ".o")
        return " ".join(obj_tokens)

    def addCompileProfile(self, compile_profile: CompileProfile) -> None:
        self.setCompileProfiles([*self.compile_profiles, compile_profile])

    def addRelSource(self, rel_source: str) -> None:
        self.setRelSources([*self.rel_sources, rel_source])

    def toJsonObject(self) -> dict[str, Any]:
        return {
            "output_makefile": self.output_makefile,
            "compile_profiles": [
                compile_profile.toJsonObject()
                for compile_profile in self.compile_profiles
            ],
            "link_compiler": self.link_compiler,
            "link_flags": self.link_flags,
            "run_args": self.run_args,
            "bin_name": self.bin_name,
            "rel_sources": self.rel_sources,
            "obj_expr": self.obj_expr,
        }

    @classmethod
    def _getObjectFromJson(cls, data: Any, errors: JsonErrorsList) -> dict[str, Any]:
        if not isinstance(data, dict):
            errors.add("Makefile config entry must be a JSON object.")
            return {}
        return data

    @classmethod
    def _getRequiredStringFieldFromJson(
        cls,
        data: dict[str, Any],
        key: str,
        errors: JsonErrorsList,
    ) -> str:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.add(f"Makefile config entry '{key}' must be a non-empty string.")
            return ""
        return value

    @classmethod
    def _getStringFieldFromJson(
        cls,
        data: dict[str, Any],
        key: str,
        errors: JsonErrorsList,
    ) -> str:
        value = data.get(key)
        if not isinstance(value, str):
            errors.add(f"Makefile config entry '{key}' must be a string.")
            return ""
        return value

    @classmethod
    def getOutputMakefileFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getRequiredStringFieldFromJson(data, "output_makefile", errors)

    @classmethod
    def getCompileProfilesFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> list[CompileProfile]:
        compile_profiles_data = data.get("compile_profiles")
        if not isinstance(compile_profiles_data, list):
            errors.add("Makefile config entry 'compile_profiles' must be a list.")
            return []

        compile_profiles: list[CompileProfile] = []
        for profile_index, profile_data in enumerate(compile_profiles_data):
            try:
                compile_profiles.append(CompileProfile.fromJsonObject(profile_data))
            except JsonValidationError as error:
                errors.extend(
                    [
                        f"compile_profiles[{profile_index}]: {message}"
                        for message in error.errors
                    ]
                )
        return compile_profiles

    @classmethod
    def getLinkCompilerFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getRequiredStringFieldFromJson(data, "link_compiler", errors)

    @classmethod
    def getLinkFlagsFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getStringFieldFromJson(data, "link_flags", errors)

    @classmethod
    def getRunArgsFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getStringFieldFromJson(data, "run_args", errors)

    @classmethod
    def getBinNameFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getRequiredStringFieldFromJson(data, "bin_name", errors)

    @classmethod
    def getRelSourcesFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> list[str]:
        rel_sources_data = data.get("rel_sources")
        if not isinstance(rel_sources_data, list):
            errors.add("Makefile config entry 'rel_sources' must be a list of strings.")
            return []

        rel_sources: list[str] = []
        for rel_source_index, rel_source in enumerate(rel_sources_data):
            if not isinstance(rel_source, str) or not rel_source.strip():
                errors.add(
                    f"rel_sources[{rel_source_index}] must be a non-empty string."
                )
                continue
            rel_sources.append(rel_source)
        return rel_sources

    @classmethod
    def getObjExprFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        return cls._getRequiredStringFieldFromJson(data, "obj_expr", errors)

    @classmethod
    def getErrorsFromJson(cls, data: Any) -> JsonErrorsList:
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            return errors

        cls.getOutputMakefileFromJson(json_object, errors)
        cls.getCompileProfilesFromJson(json_object, errors)
        cls.getLinkCompilerFromJson(json_object, errors)
        cls.getLinkFlagsFromJson(json_object, errors)
        cls.getRunArgsFromJson(json_object, errors)
        cls.getBinNameFromJson(json_object, errors)
        cls.getRelSourcesFromJson(json_object, errors)
        cls.getObjExprFromJson(json_object, errors)
        return errors

    @classmethod
    def fromJsonObject(cls, data: Any) -> "MakefileConfigEntry":
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        output_makefile = cls.getOutputMakefileFromJson(json_object, errors)
        compile_profiles = cls.getCompileProfilesFromJson(json_object, errors)
        link_compiler = cls.getLinkCompilerFromJson(json_object, errors)
        link_flags = cls.getLinkFlagsFromJson(json_object, errors)
        run_args = cls.getRunArgsFromJson(json_object, errors)
        bin_name = cls.getBinNameFromJson(json_object, errors)
        rel_sources = cls.getRelSourcesFromJson(json_object, errors)
        obj_expr = cls.getObjExprFromJson(json_object, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        return cls(
            output_makefile=output_makefile,
            compile_profiles=compile_profiles,
            link_compiler=link_compiler,
            link_flags=link_flags,
            run_args=run_args,
            bin_name=bin_name,
            rel_sources=rel_sources,
            obj_expr=obj_expr,
        )
