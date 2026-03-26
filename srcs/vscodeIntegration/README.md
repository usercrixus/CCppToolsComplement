# CCppToolsComplement

<p align="center">
  <img src="resources/demo-promo.gif" alt="Demo of launch creation and debugger flow" />
</p>

CCppToolsComplement is a Visual Studio Code extension that helps manage and debug C and C++ programs from a workspace-level `.vscode/makefileConfig.json` file.

It is designed for projects that generate build and debug configuration from that JSON file, then use VS Code and the C/C++ extension to launch the debugger.


## Features

- Adds the command `CCppToolsComplement: Generate and Debug Current File`.
- Shows the command in the top-right corner of the editor when a `c` or `cpp` file is active : <img src="resources/play-dark.png" alt="Play icon" width="14" height="14" />
- Reads program entries from `.vscode/makefileConfig.json`.
- Lets you create a new program entry from inside VS Code.
- Lets you update run arguments, compile flags, and link flags for an existing entry.
- Starts the debugger through `ms-vscode.cpptools`.

### Menu Overview

Stage 1: pick an existing program entry or create a new launch.

<p align="center">
  <img src="resources/menu01.png" alt="First menu showing existing entries and the create new launch action" />
</p>

Stage 2: manage the selected entry, including launch, arguments, and flags.

<p align="center">
  <img src="resources/menu02.png" alt="Second menu showing launch, arguments, and flags actions for one entry" />
</p>


## Prerequisites

Before using the extension, make sure the following are available:

1. Visual Studio Code `1.85.0` or later.
2. The Microsoft C/C++ extension: `ms-vscode.cpptools`.
3. A Python interpreter available as `python3`, or another executable configured through the `ccppToolsComplement.pythonPath` setting.
4. A folder opened as a VS Code workspace.

This extension works against the first workspace folder and expects project configuration files under that folder.


## How To Use

1. Open your project folder in VS Code.
2. Open a `.c` or `.cpp` file.
3. Click the editor title button : <img src="resources/play-dark.png" alt="Play icon" width="14" height="14" />
4. Pick an existing program entry, or choose `Create new launch`.

### Create a New Launch

When you choose `Create new launch`, the extension asks for:

- `Main path`
- `Program name`
- `Run arguments`
- `Binary name`

It then creates a new entry in `.vscode/makefileConfig.json`, asks for build flags, and regenerates the related VS Code integration files.

### Manage an Existing Entry

For each existing program entry, the extension offers:

- `Launch program`
  Build if needed, then start debugging.
- `Launch re`
  Force a rebuild, then start debugging.
- `Set args`
  Update the runtime argument string stored in `.vscode/makefileConfig.json`.
- `Set compile flags`
  Edit compile flags for each detected compile profile.
- `Set link flags`
  Edit linker flags.
- `Delete entry`
  Remove the selected program entry.

## Extension Setting

### `ccppToolsComplement.pythonPath`

Path or command name for the Python executable used to run the bundled backend scripts.

Default:

```json
{
  "ccppToolsComplement.pythonPath": "python3"
}
```

Set this if your system uses a different Python command, such as `python`.

## Notes

- The extension bundles its backend Python modules inside the published package.
- The debugger launch is delegated to the C/C++ extension.
- The extension validates `.vscode/makefileConfig.json` before reading program entries.

## Release / Packaging

This README is intended to be the Marketplace-facing description for the extension. Packaging and publishing steps are documented separately in the repository.
