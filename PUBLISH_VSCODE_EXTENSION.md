# Publish VS Code Extension

This file describes the concrete steps to package and publish the VS Code extension in this repository.

Extension root:

`srcs/vscodeIntegration`

Marketplace identity currently declared in the manifest:

- publisher: `achaisne`
- name: `ccpp-tools-complement`
- version: `0.0.1`

## 1. Prepare the repository

Before the first public release, clean up the repository so the packaged extension and git history are predictable.

Do these checks:

1. Make sure the extension works from `srcs/vscodeIntegration`.
2. Make sure the README in `srcs/vscodeIntegration/README.md` explains what the extension does, how to use it, and any prerequisites.
3. Confirm the packaged files are only the ones you want to ship. This is controlled by the `files` field in `srcs/vscodeIntegration/package.json`.

## 2. Improve `package.json` before first public publish

Minimal example:

```json
{
  "icon": "resources/icon.png",
  "license": "MIT",
  "keywords": ["c", "cpp", "makefile", "debug", "cpptools"],
  "repository": {
    "type": "git",
    "url": "https://github.com/<you>/<repo>.git"
  },
  "homepage": "https://github.com/<you>/<repo>",
  "bugs": {
    "url": "https://github.com/<you>/<repo>/issues"
  }
}
```

## 3. Validate the extension locally

From the project root:

```bash
cd srcs/vscodeIntegration
```

Check the manifest and packaging inputs:

1. Verify `main` points to the real entry point: `./frontend/extension.js`
2. Verify `files` includes:
   - `frontend/**`
   - `backend/**`
   - `resources/**`
   - `README.md`
   - `package.json`
3. Verify `publisher` is the exact Marketplace publisher you own.
4. Verify `version` is the version you want to publish.

Then run the extension locally in VS Code:

1. Open `srcs/vscodeIntegration` in VS Code.
2. Press `F5` to start an Extension Development Host.
3. In the Extension Development Host, open the real project root:
   `/home/achaisne/Documents/CCppToolsComplement`
4. Open a `.c` or `.cpp` file.
5. Run `CCppToolsComplement: Generate and Debug Current File`.

This matters because the extension logic expects the opened workspace to be the real project root.

## 4. Install the publishing tool

Install `vsce` once:

```bash
npm install -g @vscode/vsce
```

Check it works:

```bash
vsce --version
```

## 5. Create the Marketplace publisher

If you have not already done it:

1. Create a publisher in the Visual Studio Marketplace.
2. Make sure the publisher ID matches the `publisher` field in `srcs/vscodeIntegration/package.json`.
3. Create a Personal Access Token for publishing.

If the publisher ID does not match, update `package.json` before publishing.

## 6. Build a `.vsix` package

From root

```bash
npm install --save-dev @vscode/vsce
```

From `srcs/vscodeIntegration`:

```bash
npx vsce package
```

then to check the result (relace the x)
```bash
unzip ccpp-tools-complement-x.x.x.vsix -d ccpp-tools-complement-x.x.x
```


Expected result:

- a file like `ccpp-tools-complement-0.0.1.vsix`

Use this step every time before publishing. It catches packaging issues early.

## 7. Test the packaged extension

Install the generated `.vsix` in regular VS Code before public publish:

1. Open VS Code.
2. Open Extensions.
3. Use `Extensions: Install from VSIX...`
4. Select the generated `.vsix` file.
5. Test the command on a real C/C++ workspace.

Do not skip this. Packaging can behave differently from running the extension in debug mode.

## 8. Publish the extension

From `srcs/vscodeIntegration`:

```bash
vsce login achaisne
```

Paste the Marketplace Personal Access Token when asked.

Then publish:

```bash
vsce publish
```

If you changed the version manually in `package.json`, this publishes that version.

If you want `vsce` to bump the version for you:

```bash
vsce publish patch
```

Other options:

- `vsce publish minor`
- `vsce publish major`

## 9. Release checklist for every new version

For each release:

1. Update code and documentation.
2. Bump the extension version.
3. Run local validation.
4. Run `vsce package`.
5. Install and test the `.vsix`.
6. Run `vsce publish`.
7. Tag the release in git if you use version tags.

## 10. Optional: publish to Open VSX

If you want the extension available in VSCodium and other Open VSX based environments, also publish to Open VSX.

Typical tool:

```bash
npm install -g ovsx
```

Then publish with an Open VSX token. This is separate from Microsoft Marketplace publishing.

## 11. Short answer to the original question

No, `package.json` is not the only required thing.

You need:

1. A valid extension manifest in `srcs/vscodeIntegration/package.json`
2. The files referenced by that manifest
3. A Marketplace publisher account
4. A publishing token
5. `vsce` to package and publish
6. A versioning and test step before release
