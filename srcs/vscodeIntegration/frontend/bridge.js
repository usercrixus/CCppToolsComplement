const path = require("path");
const vscode = require("vscode");
const { getPathFromWorkspace } = require("./utilsVsCode");
const { runPythonModuleTask } = require("./pythonRunner");
const { getMakefileConfigJson, readJsonFile, writeJsonFile } = require("./utilsJson");

const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");
const PYTHON_MODULE_PREFIX = "srcs.script";

async function generateJson(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateJson`,
    true
  );
}

async function verifyJson(args, throwOnError = true) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  return runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.verifyJson`,
    false,
    throwOnError
  );
}

async function generateMakefile(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateMakefile`,
    false
  );
}

async function generateVscodeIntegration(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateVscodeIntegration`,
    false
  );
}

async function createLaunch(args) {
  await generateJson(args);
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
}

async function launchProgram(args) {
  const [workspaceFolder, entry, pythonBin, pythonPathRoot] = args;
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, false);
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

async function deleteEntryHelper(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.deleteEntry`,
    false,
    true,
    [String(entryIndex)]
  );
}

async function deleteAllMakefiles(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.deleteAllMakeFiles`,
    false
  );
}

async function generateAllMakefiles(args) {
  await generateMakefile(args);
}

// TODO: FROM HERE VERIFY THAT WHAT SHOULD BE BACKEND IS EFFECTIVELY BACKEND

async function updateRunArgs(args) {
  // TODO
}

async function updateCompileFlagsForProfile(args) {
  // TODO
}

async function updateLinkFlags(args) {
  // TODO
}

function getProgramNameFromEntry(entry) {
  const outputMakefile = typeof entry.output_makefile === "string" ? entry.output_makefile : "";
  const prefix = "Makefile.";
  const name = path.basename(outputMakefile);
  if (name.startsWith(prefix)) {
    const programName = name.slice(prefix.length).trim();
    if (programName && !programName.includes(".")) {
      return programName;
    }
  }
  return outputMakefile || "Unnamed program";
}

function getCompileProfileLabel(profile) {
  const compiler = typeof profile.compiler === "string" ? profile.compiler : "compiler";
  const ext = typeof profile.ext === "string" ? profile.ext : "";
  return `${compiler} ${ext}`.trim();
}

function getLaunchConfiguration(workspaceFolder, configurationName) {
  const launchPath = path.join(workspaceFolder.uri.fsPath, LAUNCH_REL_PATH);
  const launchJson = readJsonFile(launchPath);
  const configurations = Array.isArray(launchJson.configurations) ? launchJson.configurations : [];
  const configuration = configurations.find((item) => item && item.name === configurationName);
  if (!configuration) {
    throw new Error(`Launch configuration '${configurationName}' was not generated.`);
  }
  return configuration;
}

module.exports = {
  createLaunch,
  generateJson,
  verifyJson,
  generateMakefile,
  generateVscodeIntegration,
  launchProgram,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags,
  deleteEntry,
  deleteAllMakefiles,
  generateAllMakefiles,
  getProgramNameFromEntry,
  getCompileProfileLabel
};
