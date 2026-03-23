from typing import TypedDict


class CompileProfile(TypedDict):
    ext: str
    compiler: str
    flags: str


class MakefileConfigEntry(TypedDict):
    output_makefile: str
    compile_profiles: list[CompileProfile]
    link_compiler: str
    link_flags: str
    run_args: str
    bin_name: str
    rel_sources: list[str]
    obj_expr: str


def makeEmptyCompileProfile() -> CompileProfile:
    return {
        "ext": "",
        "compiler": "",
        "flags": "",
    }


def makeEmptyMakefileConfigEntry() -> MakefileConfigEntry:
    return {
        "output_makefile": "",
        "compile_profiles": [],
        "link_compiler": "",
        "link_flags": "",
        "run_args": "",
        "bin_name": "",
        "rel_sources": [],
        "obj_expr": "",
    }
