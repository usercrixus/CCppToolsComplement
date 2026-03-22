const { runPythonModuleTask } = require("./pythonRunner");

const PYTHON_MODULE_PREFIX = "srcs.script";

async function generateJson(args) {
  const [workspaceFolder, moduleArgs, pythonBin, pythonPathRoot] = args;
  if (!Array.isArray(moduleArgs)) {
    throw new Error("generateJson module arguments must be an array.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateJson`,
    false,
    true,
    moduleArgs
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

async function updateRunArgsHelper(args) {
  const [workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  if (typeof newArgs !== "string") {
    throw new Error("New run arguments must be a string.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.updateRunArgs`,
    false,
    true,
    [String(entryIndex), newArgs]
  );
}

async function updateCompileFlagsForProfileHelper(args) {
  const [workspaceFolder, entryIndex, profileIndex, newFlags, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  if (!Number.isInteger(profileIndex) || profileIndex < 0) {
    throw new Error("Selected compile profile index is invalid.");
  }
  if (typeof newFlags !== "string") {
    throw new Error("New compile flags must be a string.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.updateCompileFlagsForProfile`,
    false,
    true,
    [String(entryIndex), String(profileIndex), newFlags]
  );
}

async function updateLinkFlagsHelper(args) {
  const [workspaceFolder, entryIndex, newFlags, pythonBin, pythonPathRoot] = args;
  if (!Number.isInteger(entryIndex) || entryIndex < 0) {
    throw new Error("Selected program index is invalid.");
  }
  if (typeof newFlags !== "string") {
    throw new Error("New link flags must be a string.");
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.updateLinkFlags`,
    false,
    true,
    [String(entryIndex), newFlags]
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

module.exports = {
  generateJson,
  verifyJson,
  generateMakefile,
  generateVscodeIntegration,
  deleteEntryHelper,
  updateRunArgsHelper,
  updateCompileFlagsForProfileHelper,
  updateLinkFlagsHelper,
  deleteAllMakefiles
};
