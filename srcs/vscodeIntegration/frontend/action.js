const vscode = require("vscode");
const { generateJson, generateMakefile, generateVscodeIntegration, deleteEntryHelper, updateRunArgsHelper, deleteAllMakefiles } = require("./bridge");
const { getMakefileConfigJson } = require("./utilsJson");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("./utilsOthers");
const { showFormBox } = require("./boxes/formBox");

async function createLaunch(args) {
  await generateJson(args);
  await regenerateLaunchFiles(args, true);
}

async function launchProgram(args) {
  const [workspaceFolder, entry] = args;
  const launchConfig = getLaunchConfiguration(workspaceFolder, getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

async function deleteEntry(args) {
  await deleteEntryHelper(args);
  await deleteAllMakefiles(args);
  await generateAllMakefiles(args);
}

async function generateAllMakefiles(args) {
  await generateMakefile(args);
}

async function regenerateLaunchFiles(args, regenerateMakefiles) {
  if (regenerateMakefiles) {
    await generateMakefile(args);
  }
  await generateVscodeIntegration(args);
}

async function updateRunArgs(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }

  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  if (!entry) {
    throw new Error(`Entry index ${entryIndex} is out of range.`);
  }

  const currentRunArgs = typeof entry.run_args === "string" ? entry.run_args : "";
  const values = await showFormBox({
    panelType: "ccppToolsComplement.runArgsForm",
    title: "Update run arguments",
    description: "Edit the argument string passed to the generated launch configuration.",
    fields: [
      {
        name: "runArgs",
        label: "Run arguments",
        type: "textarea",
        presetValue: currentRunArgs,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact argument string that should be forwarded to the program."
      }
    ]
  });

  if (values === undefined) {
    return false;
  }

  const newArgs = typeof values.runArgs === "string" ? values.runArgs : "";
  await updateRunArgsHelper([workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot]);
  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
}

async function updateCompileFlagsForProfile(args) {
  // TODO
}

async function updateLinkFlags(args) {
  // TODO
}

module.exports = {
  createLaunch,
  launchProgram,
  deleteEntry,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags
};
