const path = require("path");
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
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  const values = await promptGenerateJsonArgs();
  if (values === undefined) {
    return false;
  }

  const moduleArgs = getGenerateJsonModuleArgs(workspaceFolder, values);
  await generateJson([workspaceFolder, moduleArgs, pythonBin, pythonPathRoot]);

  const resolvedOutputPath = resolveGenerateJsonOutputPath(
    workspaceFolder,
    values.mainPath.trim(),
    values.programName.trim()
  );
  const outputMakefile = normalizeConfigPath(
    path.relative(workspaceFolder.uri.fsPath, resolvedOutputPath)
  );
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entryIndex = findEntryIndexByOutputMakefile(entries, outputMakefile);
  if (entryIndex < 0) {
    throw new Error(`Created entry '${outputMakefile}' was not found in makefileConfig.json.`);
  }

  const flagsValues = await promptFlagsForEntry(entries[entryIndex]);
  if (flagsValues === undefined) {
    return false;
  }

  await updateLinkFlagsHelper([
    workspaceFolder,
    entryIndex,
    flagsValues.linkFlags ?? "",
    pythonBin,
    pythonPathRoot
  ]);

  const compileProfiles = Array.isArray(entries[entryIndex].compile_profiles)
    ? entries[entryIndex].compile_profiles
    : [];
  for (const [profileIndex] of compileProfiles.entries()) {
    await updateCompileFlagsForProfileHelper([
      workspaceFolder,
      entryIndex,
      profileIndex,
      flagsValues[`compileFlags_${profileIndex}`] ?? "",
      pythonBin,
      pythonPathRoot
    ]);
  }

  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
}

module.exports = {
  createLaunch
};
