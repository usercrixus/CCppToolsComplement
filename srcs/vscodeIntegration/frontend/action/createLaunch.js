const path = require("path");
const globals = require("../globals");
const {
  generateJson,
  setLinkFlagsHelper,
  setCompileFlagsForProfileHelper
} = require("../bridge");
const { getMakefileConfigJson } = require("../utils/various");
const { promptGenerateJsonArgs } = require("./form/promptGenerateJsonArgs");
const { promptFlagsForEntry } = require("./form/promptFlagsForEntry");
const {
  normalizeConfigPath,
  resolveGenerateJsonOutputPath,
  getGenerateJsonModuleArgs,
  findEntryIndexByOutputMakefile,
  regenerateLaunchFiles
} = require("./utils");

async function createLaunch(args) {
  const workspaceFolder = globals.workspaceFolder;
  const values = await promptGenerateJsonArgs();
  if (values === undefined) {
    return false;
  }
  const moduleArgs = getGenerateJsonModuleArgs(values);
  await generateJson(moduleArgs);
  const resolvedOutputPath = resolveGenerateJsonOutputPath(
    values.mainPath.trim(),
    values.programName.trim()
  );
  const outputMakefile = normalizeConfigPath(
    path.relative(workspaceFolder.uri.fsPath, resolvedOutputPath)
  );
  const entries = await getMakefileConfigJson();
  const entryIndex = findEntryIndexByOutputMakefile(entries, outputMakefile);
  const flagsValues = await promptFlagsForEntry(entries[entryIndex]);
  if (flagsValues === undefined) {
    return false;
  }
  await setLinkFlagsHelper(entryIndex, flagsValues.linkFlags ?? "");
  const compileProfiles = Array.isArray(entries[entryIndex].compile_profiles)
    ? entries[entryIndex].compile_profiles
    : [];
  for (const [profileIndex] of compileProfiles.entries()) {
    await setCompileFlagsForProfileHelper(
      entryIndex,
      profileIndex,
      flagsValues[`compileFlags_${profileIndex}`] ?? ""
    );
  }
  await regenerateLaunchFiles(entryIndex, true);
  return true;
}

module.exports = {
  createLaunch
};
