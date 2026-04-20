const { runPythonModuleTask } = require("./utils/pythonRunner");

async function generateJson(args) {
  await runPythonModuleTask(
    "jsonMakefileConfig.generateEntry",
    false,
    true,
    args
  );
}

async function verifyJson(args, throwOnError = true) {
  return runPythonModuleTask(
    "jsonMakefileConfig.verify",
    false,
    throwOnError
  );
}

async function generateMakefile(entryIndex) {
  await runPythonModuleTask(
    "makefile.generateMakefile",
    false,
    true,
    [String(entryIndex)]
  );
}

async function generateTask() {
  await runPythonModuleTask(
    "jsonTask.generateTask",
    false
  );
}

async function generateLaunch() {
  await runPythonModuleTask(
    "jsonLaunch.generateLaunch",
    false
  );
}

async function deleteEntryHelper(entryIndex) {
  await runPythonModuleTask(
    "jsonMakefileConfig.deleteEntry",
    false,
    true,
    [String(entryIndex)]
  );
}

async function deleteTask(programName) {
  await runPythonModuleTask(
    "jsonTask.deleteTask",
    false,
    true,
    [String(programName)]
  );
}

async function deleteLaunch(programName) {
  await runPythonModuleTask(
    "jsonLaunch.deleteLaunch",
    false,
    true,
    [String(programName)]
  );
}

async function setRunArgsHelper(entryIndex, newArgs) {
  await runPythonModuleTask(
    "jsonMakefileConfig.setEntry",
    false,
    true,
    [String(entryIndex), `--run-args=${newArgs}`]
  );
}

async function setCompileFlagsForProfileHelper(entryIndex, profileIndex, newFlags) {
  await runPythonModuleTask(
    "jsonMakefileConfig.setEntry",
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
    "jsonMakefileConfig.setEntry",
    false,
    true,
    [String(entryIndex), `--link-flags=${newFlags}`]
  );
}

async function refreshEntrySourcesHelper(entryIndex, relSourcesJson) {
  return runPythonModuleTask(
    "jsonMakefileConfig.setEntry",
    false,
    false,
    [String(entryIndex), `--rel-sources-json=${relSourcesJson}`]
  );
}

async function setJsonSettingsFileExcludeHelper(fileExcludeExts) {
  await runPythonModuleTask(
    "jsonSettings.setJsonSettings",
    false,
    true,
    [`--file-exclude-exts=${fileExcludeExts}`]
  );
}

async function deleteMakefile(entryIndex) {
  await runPythonModuleTask(
    "makefile.deleteMakefile",
    false,
    true,
    [String(entryIndex)]
  );
}

async function setWallpaper() {
  await runPythonModuleTask(
    "setWallpaper",
    false,
    true
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
  setJsonSettingsFileExcludeHelper,
  deleteMakefile,
  setWallpaper
};
