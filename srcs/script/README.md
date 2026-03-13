# Script Usage

Run commands from the project root.

## 1) Create/Update `.vscode/makefileConfig.json`

```bash
python3 srcs/script/generateJson.py
```

Interactive prompts:
- `Enter your main path` (example: `src/main.cpp`)
- `Enter program name` (example: `myprog`)
- `Enter run args (optional)` (example: `--verbose 42`)
- `Enter binary name (default: <program>.out)` (example: `myprog.out`)
- `Enter output Makefile path (leave empty for default)` (example: `src/Makefile.myprog`)
- `Enter flags for <compiler>` (example: `-Wall -Wextra -Werror -MMD -MP`)

## 2) Verify config

```bash
python3 srcs/script/verifyMakefileConfig.py
```

## 3) Generate Makefiles from JSON

```bash
python3 srcs/script/generateMakefileFromJson.py
```

Optional custom config path:

```bash
python3 srcs/script/generateMakefileFromJson.py .vscode/makefileConfig.json
```

## 4) Generate VSCode tasks/launch

```bash
python3 srcs/script/generateVscodeIntegrationFromJson.py
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
    "link_flags": "-Wall -Wextra -Werror -MMD -MP",
    "run_args": "--verbose 42",
    "bin_name": "myprog.out",
    "rel_sources": [
      "main.cpp",
      "utils/helpers.cpp"
    ],
    "obj_expr": "main.o utils/helpers.o"
  }
]
```
