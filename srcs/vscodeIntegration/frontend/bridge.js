const { runPythonModuleTask } = require("./utils/pythonRunner");

const PYTHON_MODULE_PREFIX = "srcs.script";

async function generateJson(args) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.generateJson`,
    false,
    true,
    args
  );
}

async function verifyJson(args, throwOnError = true) {
  return runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.verifyJson`,
    false,
    throwOnError
  );
}

async function generateMakefile() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.generateMakefile`,
    false
  );
}

async function generateVscodeIntegration() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.generateVscodeIntegration`,
    false
  );
}

async function deleteEntryHelper(entryIndex) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.deleteEntry`,
    false,
    true,
    [String(entryIndex)]
  );
}

async function setRunArgsHelper(entryIndex, newArgs) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.setRunArgs`,
    false,
    true,
    [String(entryIndex), newArgs]
  );
}

async function setCompileFlagsForProfileHelper(entryIndex, profileIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.setCompileFlagsForProfile`,
    false,
    true,
    [String(entryIndex), String(profileIndex), newFlags]
  );
}

async function setLinkFlagsHelper(entryIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.setLinkFlags`,
    false,
    true,
    [String(entryIndex), newFlags]
  );
}

async function setJsonSourcesHelper(entryIndex) {
  return runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.setJsonSources`,
    false,
    false,
    [String(entryIndex)]
  );
}

async function deleteAllMakefiles() {
  await runPythonModuleTask(
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
  setRunArgsHelper,
  setCompileFlagsForProfileHelper,
  setLinkFlagsHelper,
  setJsonSourcesHelper,
  deleteAllMakefiles
};
