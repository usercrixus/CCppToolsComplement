const path = require("path");
const { generateMakefile, generateVscodeIntegration } = require("../bridge");

function normalizeConfigPath(filePath) {
  return filePath.split(path.sep).join("/");
}

function resolveGenerateJsonOutputPath(workspaceFolder, mainPathInput, programName) {
  const resolvedMainPath = path.isAbsolute(mainPathInput)
    ? mainPathInput
    : path.resolve(workspaceFolder.uri.fsPath, mainPathInput);
  return path.resolve(path.dirname(resolvedMainPath), `Makefile.${programName}`);
}

function getGenerateJsonModuleArgs(workspaceFolder, values) {
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

async function generateAllMakefiles(args) {
  await generateMakefile(args);
}

async function regenerateLaunchFiles(args, regenerateMakefiles) {
  if (regenerateMakefiles) {
    await generateMakefile(args);
  }
  await generateVscodeIntegration(args);
}

module.exports = {
  normalizeConfigPath,
  resolveGenerateJsonOutputPath,
  getGenerateJsonModuleArgs,
  findEntryIndexByOutputMakefile,
  generateAllMakefiles,
  regenerateLaunchFiles
};
