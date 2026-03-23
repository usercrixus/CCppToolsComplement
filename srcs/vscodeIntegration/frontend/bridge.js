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

async function updateRunArgsHelper(entryIndex, newArgs) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.updateRunArgs`,
    false,
    true,
    [String(entryIndex), newArgs]
  );
}

async function updateCompileFlagsForProfileHelper(entryIndex, profileIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.updateCompileFlagsForProfile`,
    false,
    true,
    [String(entryIndex), String(profileIndex), newFlags]
  );
}

async function updateLinkFlagsHelper(entryIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.updateLinkFlags`,
    false,
    true,
    [String(entryIndex), newFlags]
  );
}

async function updateJsonSourcesHelper(entryIndex) {
  return runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.updateJsonSources`,
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
  updateRunArgsHelper,
  updateCompileFlagsForProfileHelper,
  updateLinkFlagsHelper,
  updateJsonSourcesHelper,
  deleteAllMakefiles
};
