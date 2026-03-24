const { runPythonModuleTask } = require("./utils/pythonRunner");

const PYTHON_MODULE_PREFIX = "srcs.script";

async function generateJson(args) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.generateEntry`,
    false,
    true,
    args
  );
}

async function verifyJson(args, throwOnError = true) {
  return runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.verify`,
    false,
    throwOnError
  );
}

async function generateMakefile() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.makefile.generateMakefile`,
    false
  );
}

async function generateTask() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonTask.generateTask`,
    false
  );
}

async function generateLaunch() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonLaunch.generateLaunch`,
    false
  );
}

async function deleteEntryHelper(entryIndex) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.deleteEntry`,
    false,
    true,
    [String(entryIndex)]
  );
}

async function deleteTask(programName) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonTask.deleteTask`,
    false,
    true,
    [String(programName)]
  );
}

async function deleteLaunch(programName) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonLaunch.deleteLaunch`,
    false,
    true,
    [String(programName)]
  );
}

async function setRunArgsHelper(entryIndex, newArgs) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.setEntry`,
    false,
    true,
    [String(entryIndex), `--run-args=${newArgs}`]
  );
}

async function setCompileFlagsForProfileHelper(entryIndex, profileIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.setEntry`,
    false,
    true,
    [
      String(entryIndex),
      "--compile-profile-index",
      String(profileIndex),
      `--link-flag-compile-profiles=${newFlags}`
    ]
  );
}

async function setLinkFlagsHelper(entryIndex, newFlags) {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.setEntry`,
    false,
    true,
    [String(entryIndex), `--link-flags=${newFlags}`]
  );
}

async function refreshEntrySourcesHelper(entryIndex, relSourcesJson) {
  return runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.jsonMakefileConfig.setEntry`,
    false,
    false,
    [String(entryIndex), `--rel-sources-json=${relSourcesJson}`]
  );
}

async function deleteAllMakefiles() {
  await runPythonModuleTask(
    `${PYTHON_MODULE_PREFIX}.action.makefile.deleteAllMakeFiles`,
    false
  );
}

module.exports = {
  generateJson,
  verifyJson,
  generateMakefile,
  generateTask,
  generateLaunch,
  deleteEntryHelper,
  deleteTask,
  deleteLaunch,
  setRunArgsHelper,
  setCompileFlagsForProfileHelper,
  setLinkFlagsHelper,
  refreshEntrySourcesHelper,
  deleteAllMakefiles
};
