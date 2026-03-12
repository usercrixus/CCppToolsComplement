    ./scripts/generateVscodeMakefileIntegration.py
    ./scripts/generateMakefile.py
    ./scripts/generateMakefileFromJson.py

`generateMakefile.py` prompts:
- Enter your main path
- Enter program name (rule/sub-Makefile suffix)
- Enter run args (optional)
- Enter binary name (optional, default `<program>.out`)
- Enter output Makefile path (optional, default `<main_dir>/Makefile.<program>`)
- Enter flags for each detected compiler (`gcc`, `g++`, ...), one prompt per compiler found in sources

Behavior:
- Updates a single config file at `.vscode/makefileConfig.json`.
- The config file contains a JSON array, one object per program/sub-Makefile.
- Auto-discovers `SRCS` from local includes.
- Stores compile profile rules by extension/compiler/flags (supports mixed C/C++).

`generateMakefileFromJson.py`:
- Reads `.vscode/makefileConfig.json` (or a provided path).
- Generates a standardized sub-Makefile (`COMPILER`, `FLAGS`, `ARGS`, `BIN`, `SRCS`, `OBJS`, `DEPS`).
- Auto-updates/creates the parent `Makefile` in the same directory with delegated rules:
  - `all`
  - one build rule and one run rule per program (e.g. `basicsBuild`, `basicsRun`)
  - `clean`, `fclean`, `re`, `.PHONY`

`generateVscodeMakefileIntegration.py`:
- Reads `.vscode/makefileConfig.json` and maps each entry to VSCode task+launch.
