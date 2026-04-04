# `Classes`

Field comments for each structure in [Classes](/home/achaisne/Documents/CCppToolsComplement/srcs/vscodeIntegration/backend/sourcesHeadersMatcher/Classes).

## `Recurrence`

```python
@dataclass(slots=True)
class Recurrence:
    source: str   # Path of the file where the prototype was found or referenced.
    times: int    # Number of occurrences in that file.
```

## `ProtoMatch`

```python
@dataclass(slots=True)
class ProtoMatch:
    implementation: str          # Full implementation or declaration text linked to the prototype.
    source: str                  # Source file considered the owner of this candidate.
    recurence: list[Recurrence]  # Per-file recurrence counters for this prototype.
    header_path: str | None      # Header path chosen for emission, or None until assigned.
```

## `ResolvedProto`

```python
@dataclass(slots=True)
class ResolvedProto:
    classes: set[str]    # All discovered class declarations.
    functions: set[str]  # All discovered function prototypes.
    macros: set[str]     # All discovered macro definitions.
    structs: set[str]    # All discovered struct declarations.
    typedefs: set[str]   # All discovered typedef or using declarations.
```

## `TraversalResult`

```python
@dataclass(slots=True)
class TraversalResult:
    proto: ResolvedProto                # Aggregated declarations found during traversal.
    generated_headers: GeneratedHeaders # Prototype -> list of candidate matches.
    source_texts_by_path: SourceTextsByPath  # Source file contents indexed by path.
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
GeneratedHeaders = dict[str, list[ProtoMatch]]
# Maps one prototype string to all candidate matches found for it.

SourceTextsByPath = dict[str, str]
# Maps a file path to the full source text loaded from that file.

HeaderMap = dict[str, list[str]]
# Maps a header path to the declarations that should be written into it.

IncludeMap = dict[str, set[str]]
# Maps a source path to the set of header paths it should include.
```
