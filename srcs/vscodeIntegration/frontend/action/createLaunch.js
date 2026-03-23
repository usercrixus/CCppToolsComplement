const path = require("path");
const globals = require("../globals");
const {
  generateJson,
  updateLinkFlagsHelper,
  updateCompileFlagsForProfileHelper
} = require("../bridge");
const { getMakefileConfigJson } = require("../utilsJson");
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
  await updateLinkFlagsHelper(entryIndex, flagsValues.linkFlags ?? "");
  const compileProfiles = Array.isArray(entries[entryIndex].compile_profiles)
    ? entries[entryIndex].compile_profiles
    : [];
  for (const [profileIndex] of compileProfiles.entries()) {
    await updateCompileFlagsForProfileHelper(
      entryIndex,
      profileIndex,
      flagsValues[`compileFlags_${profileIndex}`] ?? ""
    );
  }
  await regenerateLaunchFiles(true);
  return true;
}

module.exports = {
  createLaunch
};
