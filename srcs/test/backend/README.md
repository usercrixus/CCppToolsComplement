# Test Usage

Run commands from the project root.

## Integration test for script generation

`srcs/test/backend/script/main.py` exercises the full script pipeline against the sample C programs in `srcs/test/backend/cProgram`.

Run it with:

```bash
python3 srcs/test/backend/script/main.py
```

What it does:
- removes generated artifacts from `.vscode/` and `srcs/test/backend/cProgram/`
- updates `srcs/test/backend/cProgram/subfolder/header.h`
- runs `srcs.script.generateJson` for both sample programs
- runs `srcs.script.generateMakefile`
- builds and executes both generated programs
- checks the runtime output for two successive passes
- runs `srcs.script.generateVscodeIntegration`

Files used by the test:
- `srcs/test/backend/cProgram/main1.c`
- `srcs/test/backend/cProgram/main2.c`
- `srcs/test/backend/cProgram/one.c`
- `srcs/test/backend/cProgram/subfolder/two.c`
- `srcs/test/backend/cProgram/subfolder/header.h`

The test is intended as an end-to-end validation of:
- source discovery
- JSON generation
- Makefile generation
- rebuild behavior after a header change
- VSCode task and launch generation

## sourcesHeadersMatcher fixture project

`srcs/test/backend/sourcesHeadersMatcher/project` is a small C fixture tree for
`srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py`.

Run it with:

```bash
python3 srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py srcs/test/backend/sourcesHeadersMatcher/project
```

What it contains:
- declarations grouped in `project/catalog/declarations.c`
- implementations split across `project/services/` and `project/config/`
- local headers already present in `project/config/` and `project/services/`
- one extra math pair `adjust.h` / `adjust.c` to widen coverage
- a macro, forward-declared struct and typedef inside `project/config/feature.c`
