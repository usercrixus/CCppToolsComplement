from dataclasses import dataclass, field


@dataclass
class JsonErrorsList:
    errors: list[str] = field(default_factory=list)

    def add(self, error: str) -> None:
        self.errors.append(error)

    def extend(self, errors: list[str]) -> None:
        self.errors.extend(errors)

    def isEmpty(self) -> bool:
        return not self.errors


@dataclass
class JsonValidationError(ValueError):
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        super().__init__("\n".join(self.errors))
