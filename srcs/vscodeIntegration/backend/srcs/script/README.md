# Script Usage

Run commands from the project root.

## 1) Create or update `.vscode/makefileConfig.json`

```bash
python3 -m srcs.script.generateJson
```

Interactive prompts:
- `Enter your main path` (example: `src/main.cpp`)
- `Enter program name` (example: `myprog`)
- `Enter run args (optional)` (example: `--verbose 42`)
- `Enter binary name (default: <program>.out)` (example: `myprog.out`)
- `Enter output Makefile path (leave empty for default)` (example: `src/Makefile.myprog`)
- `Enter flags for <compiler>` for each detected compile compiler
- `Enter link flags for <compiler>` for the selected linker

## 2) Verify config

```bash
python3 -m srcs.script.verifyJson
```

## 3) Generate Makefiles from JSON

```bash
python3 -m srcs.script.generateMakefileFromJson
```

## 4) Generate VSCode tasks/launch

```bash
python3 -m srcs.script.generateVscodeIntegrationFromJson
```

## 5) Delete one config entry

Delete by `output_makefile`:

```bash
python3 -m srcs.script.deleteEntry src/Makefile.myprog
```

## Base `makefileConfig.json` structure

File: `.vscode/makefileConfig.json` (JSON array of entries)

```json
[
  {
    "output_makefile": "/absolute/path/to/project/src/Makefile.myprog",
    "compile_profiles": [
      {
        "ext": ".cpp",
        "compiler": "g++",
        "flags": "-Wall -Wextra -Werror -MMD -MP"
      },
      {
        "ext": ".c",
        "compiler": "gcc",
        "flags": "-Wall -Wextra -Werror -MMD -MP"
      }
    ],
    "link_compiler": "g++",
    "link_flags": "-g3 -O0",
    "run_args": "--verbose 42",
    "bin_name": "myprog.out",
    "rel_sources": [
      "main.cpp",
      "one.c",
      "utils/helpers.cpp"
    ],
    "obj_expr": "main.o one.o utils/helpers.o"
  }
]
```
