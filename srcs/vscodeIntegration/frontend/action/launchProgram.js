const vscode = require("vscode");
const globals = require("../globals");
const {
  refreshEntrySourcesHelper,
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

async function launchProgram(args) {
  const [entryIndex] = args;
  const entriesBefore = await getMakefileConfigJson();
  const previousEntry = entriesBefore[entryIndex];
  const refreshStatus = await refreshEntrySourcesHelper(
    entryIndex,
    JSON.stringify(previousEntry.rel_sources ?? [])
  );
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];

  if (refreshStatus === 1) {
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
  await regenerateLaunchFiles(entryIndex, true);
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
