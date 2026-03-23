const vscode = require("vscode");
const globals = require("../globals");
const {
  setJsonSourcesHelper,
  setLinkFlagsHelper,
  setCompileFlagsForProfileHelper
} = require("../bridge");
const {
  getMakefileConfigJson,
  getProgramNameFromEntry,
  getLaunchConfiguration
} = require("../utils/various");
const { promptFlagsForEntry } = require("./form/promptFlagsForEntry");
const { regenerateLaunchFiles } = require("./utils");

async function trySetJsonSources(entryIndex) {
  const status = await setJsonSourcesHelper(entryIndex);
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  if (status === 1) {
    const flagsValues = await promptFlagsForEntry(entry);
    if (flagsValues === undefined) {
      return false;
    }
    await setLinkFlagsHelper(entryIndex, flagsValues.linkFlags ?? "");
    const compileProfiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles : [];
    for (const [profileIndex] of compileProfiles.entries()) {
      await setCompileFlagsForProfileHelper(
        entryIndex,
        profileIndex,
        flagsValues[`compileFlags_${profileIndex}`] ?? ""
      );
    }
  }
  return entry;
}

async function launchProgram(args) {
  const [entryIndex] = args;
  const entry = await trySetJsonSources(entryIndex);
  if (entry === false) {
    return false;
  }
  await regenerateLaunchFiles(true);
  const launchConfig = getLaunchConfiguration(getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(globals.workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

module.exports = {
  launchProgram
};
