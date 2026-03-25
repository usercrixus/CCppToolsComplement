const path = require("path");
const { generateLaunch, generateMakefile, generateTask } = require("../bridge");
const globals = require("../globals");

function normalizeConfigPath(filePath) {
  return filePath.split(path.sep).join("/");
}

function resolveGenerateJsonOutputPath(mainPathInput, programName) {
  const workspaceFolder = globals.workspaceFolder;
  const resolvedMainPath = path.isAbsolute(mainPathInput)
    ? mainPathInput
    : path.resolve(workspaceFolder.uri.fsPath, mainPathInput);
  return path.resolve(path.dirname(resolvedMainPath), `Makefile.${programName}`);
}

function getGenerateJsonModuleArgs(values) {
  const mainPath = values.mainPath.trim();
  const programName = values.programName.trim();
  const runArgs = values.runArgs ?? "";
  const binName = values.binName ?? "";
  const moduleArgs = [
    "--main-path",
    mainPath,
    "--program-name",
    programName
  ];
  if (runArgs) {
    moduleArgs.push("--run-args", runArgs);
  }
  if (binName) {
    moduleArgs.push("--bin-name", binName);
  }
  return moduleArgs;
}

function findEntryIndexByOutputMakefile(entries, outputMakefile) {
  return entries.findIndex((entry) => entry?.output_makefile === outputMakefile);
}

async function generateOneMakefile(entryIndex) {
  await generateMakefile(entryIndex);
}

async function regenerateLaunchFiles(entryIndex, regenerateMakefileForEntry) {
  if (regenerateMakefileForEntry) {
    await generateMakefile(entryIndex);
  }
  await generateTask();
  await generateLaunch();
}

module.exports = {
  normalizeConfigPath,
  resolveGenerateJsonOutputPath,
  getGenerateJsonModuleArgs,
  findEntryIndexByOutputMakefile,
  generateOneMakefile,
  regenerateLaunchFiles
};
