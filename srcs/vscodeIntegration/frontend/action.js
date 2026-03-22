const vscode = require("vscode");
const { generateJson, generateMakefile, generateVscodeIntegration, deleteEntryHelper, deleteAllMakefiles } = require("./bridge");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("./utilsOthers");

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
  // TODO
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
