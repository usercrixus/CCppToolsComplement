from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CompileProfile:
    ext: str = ""
    compiler: str = ""
    flags: str = ""

    def setExt(self, ext: str) -> None:
        self.ext = ext

    def setCompiler(self, compiler: str) -> None:
        self.compiler = compiler

    def setFlags(self, flags: str) -> None:
        self.flags = flags


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
        self.setLinkCompiler(self.compile_profiles.compiler)

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


def makeEmptyCompileProfile() -> CompileProfile:
    return CompileProfile()


def makeEmptyMakefileConfigEntry() -> MakefileConfigEntry:
    return MakefileConfigEntry()
