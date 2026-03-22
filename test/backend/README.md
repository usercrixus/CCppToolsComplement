# Test Usage

Run commands from the project root.

## Integration test for script generation

`test/backend/script/main.py` exercises the full script pipeline against the sample C programs in `test/backend/cProgram`.

Run it with:

```bash
python3 test/backend/script/main.py
```

What it does:
- removes generated artifacts from `.vscode/` and `test/backend/cProgram/`
- updates `test/backend/cProgram/subfolder/header.h`
- runs `srcs.script.generateJson` for both sample programs
- runs `srcs.script.generateMakefile`
- builds and executes both generated programs
- checks the runtime output for two successive passes
- runs `srcs.script.generateVscodeIntegration`

Files used by the test:
- `test/backend/cProgram/main1.c`
- `test/backend/cProgram/main2.c`
- `test/backend/cProgram/one.c`
- `test/backend/cProgram/subfolder/two.c`
- `test/backend/cProgram/subfolder/header.h`

The test is intended as an end-to-end validation of:
- source discovery
- JSON generation
- Makefile generation
- rebuild behavior after a header change
- VSCode task and launch generation
