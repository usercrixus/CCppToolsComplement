const path = require("path");
const vscode = require("vscode");
const { getPathFromWorkspace } = require("./utilsVsCode");
const { runPythonModuleTask } = require("./pythonRunner");
const { getMakefileConfigJson, readJsonFile, writeJsonFile } = require("./utilsJson");

const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");
const PYTHON_MODULE_PREFIX = "srcs.script";

async function createLaunch(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  await runPythonModuleTask(workspaceFolder, pythonBin, pythonPathRoot, `${PYTHON_MODULE_PREFIX}.generateJson`, true);
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
}

async function launchProgram(args) {
  const [workspaceFolder, entry, pythonBin, pythonPathRoot] = args;
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, false);
  const launchConfig = getLaunchConfiguration(workspaceFolder, getLaunchNameForEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}


async function deleteEntry(args) {
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
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
}

// TODO: FROM HERE VERIFY THAT WHAT SHOULD BE BACKEND IS EFFECTIVELY BACKEND

async function updateRunArgs(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const value = await vscode.window.showInputBox({
    prompt: `Run args for ${getProgramNameFromEntry(entry)}`,
    value: typeof entry.run_args === "string" ? entry.run_args : "",
    placeHolder: "--verbose 42"
  });
  if (value === undefined) {
    throw new Error("Run args update was cancelled.");
  }
  entry.run_args = value.trim();
  saveConfigEntries(entries);
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, false);
}

async function updateCompileFlagsForProfile(args) {
  const [workspaceFolder, entryIndex, profileIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const originalProfiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles : [];
  const profile = originalProfiles[profileIndex];
  if (!isObject(profile)) {
    throw new Error("Compile profile could not be updated.");
  }

  const value = await vscode.window.showInputBox({
    prompt: `Compile flags for ${getCompileProfileLabel(profile)}`,
    value: typeof profile.flags === "string" ? profile.flags : "",
    placeHolder: "-Wall -Wextra -Werror -MMD -MP"
  });
  if (value === undefined) {
    throw new Error("Compile flags update was cancelled.");
  }

  originalProfiles[profileIndex].flags = value.trim();
  saveConfigEntries(entries);
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
}

async function updateLinkFlags(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const value = await vscode.window.showInputBox({
    prompt: `Link flags for ${getProgramNameFromEntry(entry)}`,
    value: typeof entry.link_flags === "string" ? entry.link_flags : "",
    placeHolder: "-g3 -O0"
  });
  if (value === undefined) {
    throw new Error("Link flags update was cancelled.");
  }
  entry.link_flags = value.trim();
  saveConfigEntries(entries);
  await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
}

async function regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, regenerateMakefiles) {
  if (regenerateMakefiles) {
    await runPythonModuleTask(
      workspaceFolder,
      pythonBin,
      pythonPathRoot,
      `${PYTHON_MODULE_PREFIX}.generateMakefileFromJson`,
      false
    );
  }
  await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.generateVscodeIntegrationFromJson`,
    false
  );
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

function getLaunchNameForEntry(entry) {
  return `Debug graph ${getProgramNameFromEntry(entry)}`;
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

function saveConfigEntries(entries) {
  const configPath = getPathFromWorkspace(CONFIG_REL_PATH);
  writeJsonFile(configPath, entries);
}

function isObject(value) {
  return Boolean(value) && typeof value === "object";
}

module.exports = {
  createLaunch,
  launchProgram,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags,
  deleteEntry,
  getProgramNameFromEntry,
  getCompileProfileLabel
};
