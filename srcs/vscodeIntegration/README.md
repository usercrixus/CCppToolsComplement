# VSCode Extension

This folder contains the VSCode extension for the project.

## What it does

The command `CCppToolsComplement: Generate and Debug Current File`:
- opens a first quick-pick with the programs found in `.vscode/makefileConfig.json`
- for each program, opens a second quick-pick with program-specific actions
- supports `Launch program`, `Set args`, `Set compile flags`, and `Set link flags`
- writes config changes back into `.vscode/makefileConfig.json`
- regenerates Makefiles or VSCode launch integration after edits when needed
- also offers a `Create new launch` action from the first picker
- when `Create new launch` is selected, runs the bundled `srcs.script.generateJson` Python module in an integrated terminal so you can answer the prompts
- then regenerates the Makefiles and VSCode integration files

The command is also exposed from the editor title when a `c` or `cpp` file is active.

## Package the extension

From this folder:

```bash
npm install -g @vscode/vsce
vsce package
```

This produces a `.vsix` file that can be installed in VSCode.

## Notes

- The extension depends on `ms-vscode.cpptools`.
- The default Python executable is `python3`.
- You can change it through the `ccppToolsComplement.pythonPath` setting.
- The packaged extension now includes its Python scripts under `bundled/`, so it no longer depends on sibling files outside the extension folder.
