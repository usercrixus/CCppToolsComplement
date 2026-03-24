from dataclasses import dataclass
from typing import Any

from srcs.script.exception.exceptionJsonErrorsList import JsonErrorsList, JsonValidationError


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

    def toJsonObject(self) -> dict[str, str]:
        return {
            "ext": self.ext,
            "compiler": self.compiler,
            "flags": self.flags,
        }

    @classmethod
    def _getObjectFromJson(cls, data: Any, errors: JsonErrorsList) -> dict[str, Any]:
        if not isinstance(data, dict):
            errors.add("Compile profile must be a JSON object.")
            return {}
        return data

    @classmethod
    def getExtFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        ext = data.get("ext")
        if not isinstance(ext, str) or not ext.strip():
            errors.add("Compile profile 'ext' must be a non-empty string.")
            return ""
        if not ext.startswith("."):
            errors.add("Compile profile 'ext' must start with '.'.")
            return ""
        return ext

    @classmethod
    def getCompilerFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        compiler = data.get("compiler")
        if not isinstance(compiler, str) or not compiler.strip():
            errors.add("Compile profile 'compiler' must be a non-empty string.")
            return ""
        return compiler

    @classmethod
    def getFlagsFromJson(cls, data: dict[str, Any], errors: JsonErrorsList) -> str:
        flags = data.get("flags")
        if not isinstance(flags, str):
            errors.add("Compile profile 'flags' must be a string.")
            return ""
        return flags

    @classmethod
    def getErrorsFromJson(cls, data: Any) -> JsonErrorsList:
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            return errors

        cls.getExtFromJson(json_object, errors)
        cls.getCompilerFromJson(json_object, errors)
        cls.getFlagsFromJson(json_object, errors)
        return errors

    @classmethod
    def fromJsonObject(cls, data: Any) -> "CompileProfile":
        errors = JsonErrorsList()
        json_object = cls._getObjectFromJson(data, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        ext = cls.getExtFromJson(json_object, errors)
        compiler = cls.getCompilerFromJson(json_object, errors)
        flags = cls.getFlagsFromJson(json_object, errors)
        if not errors.isEmpty():
            raise JsonValidationError(errors.errors)

        return cls(
            ext=ext,
            compiler=compiler,
            flags=flags,
        )
