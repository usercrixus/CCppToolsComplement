# `Classes`

Field comments for each structure in [Classes](/home/achaisne/Documents/CCppToolsComplement/srcs/vscodeIntegration/backend/sourcesHeadersMatcher/Classes).

## `Recurrence`

```python
Recurrence = dict[str, int]
# Maps one source path to its occurrence count.
```

## `Symbol`

```python
@dataclass(slots=True)
class Symbol:
    declaration: str             # Original declaration string for this candidate.
    implementation: str          # Full implementation or declaration text linked to the prototype.
    source: str                  # Source file considered the owner of this candidate.
    recurence: Recurrence        # Per-file recurrence counters for this prototype.
    header_path: str | None      # Header path chosen for emission, or None until assigned.
```

## Derived symbols

```python
class FunctionSymbol(Symbol): ...
class MacroSymbol(Symbol): ...
class ClassSymbol(Symbol): ...
class StructSymbol(Symbol): ...
class TypedefSymbol(Symbol): ...
```

## `TraversalResult`

```python
@dataclass(slots=True)
class TraversalResult:
    symbols: dict[str, Symbol]   # Symbol name -> matched Symbol subclass instance.
```

## `RenderJob`

```python
@dataclass(slots=True)
class RenderJob:
    path: str    # Output file path to write.
    string: str  # Full rendered content for that file.
```

## `ExtractedFileStatements`

```python
@dataclass(slots=True)
class ExtractedFileStatements:
    classes: list[str]                   # Class declarations extracted from one file.
    function_implementations: list[str]  # Function implementations extracted from one file.
    macros: list[str]                    # Macro definitions extracted from one file.
    structs: list[str]                   # Struct declarations extracted from one file.
    typedefs: list[str]                  # Typedef or alias declarations extracted from one file.
```

## Referenced aliases

```python
SourceTextsByPath = dict[str, str]
# Maps a file path to the full source text loaded from that file.

Headers = dict[str, list[str]]
# Maps a header path to the declarations that should be written into it.

IncludeMap = dict[str, set[str]]
# Maps a source path to the set of header paths it should include.
```
