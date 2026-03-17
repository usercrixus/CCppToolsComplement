const fs = require("fs");
const path = require("path");
const vscode = require("vscode");
const { getWorkspaceFolder, getExtentionAbsolutePath } = require("./utils");
const { runPythonModuleTask } = require("./pythonRunner");

const COMMAND_ID = "ccppToolsComplement.generateAndDebugFromCurrentFile";
const CREATE_LAUNCH_ACTION = "ccppToolsComplement.createLaunch";
const GO_BACK_ACTION = "ccppToolsComplement.goBack";
const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");
const BUNDLED_PYTHON_ROOT = "bundled";
const PYTHON_MODULE_PREFIX = "srcs.script";
const ACTION_LAUNCH = "launch";
const ACTION_SET_ARGS = "setArgs";
const ACTION_SET_COMPILE_FLAGS = "setCompileFlags";
const ACTION_SET_LINK_FLAGS = "setLinkFlags";
let extensionContext = null;

function activate(context) {
  extensionContext = context;
  const disposable = vscode.commands.registerCommand(COMMAND_ID, async () => {
    try {
      await generateAndDebugFromCurrentFile();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(message);
    }
  });
  context.subscriptions.push(disposable);
}

function deactivate() {}

async function generateAndDebugFromCurrentFile() {
  const workspaceFolder = getWorkspaceFolder();
  const pythonBin = vscode.workspace.getConfiguration("ccppToolsComplement").get("pythonPath", "python3");
  const pythonPathRoot = getExtentionAbsolutePath(extensionContext, BUNDLED_PYTHON_ROOT);

  while (true) {
    const selection = await pickProgram(workspaceFolder);
    if (selection === CREATE_LAUNCH_ACTION) {
      await createLaunch(workspaceFolder, pythonBin, pythonPathRoot);
      continue;
    }
    const launchConfig = await handleProgramActions(workspaceFolder, selection, pythonBin, pythonPathRoot);
    if (!launchConfig) {
      continue;
    }
    const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
    if (!started) {
      throw new Error("VSCode did not start the debugger.");
    }
    return;
  }
}

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read JSON file '${filePath}'.`);
  }
}

function writeJsonFile(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function getConfigPath(workspaceFolder) {
  return path.join(workspaceFolder.uri.fsPath, CONFIG_REL_PATH);
}

function getConfigEntries(workspaceFolder) {
  const configPath = getConfigPath(workspaceFolder);
  if (!fs.existsSync(configPath)) {
    return [];
  }
  const config = readJsonFile(configPath);
  if (!Array.isArray(config)) {
    throw new Error(`Config file '${configPath}' must contain a JSON array.`);
  }
  return config.filter((entry) => entry && typeof entry === "object");
}

function saveConfigEntries(workspaceFolder, entries) {
  const configPath = getConfigPath(workspaceFolder);
  writeJsonFile(configPath, entries);
}

async function pickProgram(workspaceFolder) {
  const entries = getConfigEntries(workspaceFolder);
  const items = entries.map((entry, index) => ({
    label: getProgramNameFromEntry(entry),
    description: getProgramDescription(entry),
    entryIndex: index
  }));
  items.push({
    label: "Create new launch",
    description: "Add a new program entry and regenerate VS Code launch.json",
    entryIndex: CREATE_LAUNCH_ACTION
  });

  const selected = await vscode.window.showQuickPick(items, {
    placeHolder: "Select a program"
  });
  if (!selected) {
    throw new Error("Program selection was cancelled.");
  }
  return selected.entryIndex;
}

async function handleProgramActions(workspaceFolder, entryIndex, pythonBin, pythonPathRoot) {
  while (true) {
    const entries = getConfigEntries(workspaceFolder);
    const entry = entries[entryIndex];
    if (!entry) {
      throw new Error("Selected program no longer exists in makefileConfig.json.");
    }

    const action = await pickProgramAction(entry);
    if (action === GO_BACK_ACTION) {
      return null;
    }
    if (action === ACTION_LAUNCH) {
      await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, false);
      return getLaunchConfiguration(workspaceFolder, getLaunchNameForEntry(entry));
    }
    if (action === ACTION_SET_ARGS) {
      await updateRunArgs(workspaceFolder, entryIndex);
      await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, false);
      continue;
    }
    if (action === ACTION_SET_COMPILE_FLAGS) {
      await updateCompileFlags(workspaceFolder, entryIndex);
      await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
      continue;
    }
    if (action === ACTION_SET_LINK_FLAGS) {
      await updateLinkFlags(workspaceFolder, entryIndex);
      await regenerateLaunchFiles(workspaceFolder, pythonBin, pythonPathRoot, true);
    }
  }
}

async function pickProgramAction(entry) {
  const items = [
    {
      label: "Launch program",
      description: "Build if needed and start the debugger",
      action: ACTION_LAUNCH
    },
    {
      label: "Set args",
      description: getRunArgsDescription(entry),
      action: ACTION_SET_ARGS
    },
    {
      label: "Set compile flags",
      description: getCompileFlagsSummary(entry),
      action: ACTION_SET_COMPILE_FLAGS
    },
    {
      label: "Set link flags",
      description: typeof entry.link_flags === "string" && entry.link_flags ? entry.link_flags : "(empty)",
      action: ACTION_SET_LINK_FLAGS
    },
    {
      label: "Back",
      description: "Return to the program list",
      action: GO_BACK_ACTION
    }
  ];

  const selected = await vscode.window.showQuickPick(items, {
    placeHolder: `Select an action for ${getProgramNameFromEntry(entry)}`
  });
  if (!selected) {
    throw new Error("Program action was cancelled.");
  }
  return selected.action;
}

async function createLaunch(workspaceFolder, pythonBin, pythonPathRoot) {
  await runPythonModuleTask(workspaceFolder, pythonBin, pythonPathRoot, `${PYTHON_MODULE_PREFIX}.generateJson`, true);
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

async function updateRunArgs(workspaceFolder, entryIndex) {
  const entries = getConfigEntries(workspaceFolder);
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
  saveConfigEntries(workspaceFolder, entries);
}

async function updateCompileFlags(workspaceFolder, entryIndex) {
  const entries = getConfigEntries(workspaceFolder);
  const entry = entries[entryIndex];
  const profiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles.filter(isObject) : [];
  if (profiles.length === 0) {
    throw new Error("No compile profiles found for this program.");
  }

  let profileIndex = 0;
  if (profiles.length > 1) {
    const profileItems = profiles.map((profile, index) => ({
      label: `${typeof profile.compiler === "string" ? profile.compiler : "compiler"} ${typeof profile.ext === "string" ? profile.ext : ""}`.trim(),
      description: typeof profile.flags === "string" && profile.flags ? profile.flags : "(empty)",
      index
    }));
    const selection = await vscode.window.showQuickPick(profileItems, {
      placeHolder: `Select compile flags to edit for ${getProgramNameFromEntry(entry)}`
    });
    if (!selection) {
      throw new Error("Compile flags update was cancelled.");
    }
    profileIndex = selection.index;
  }

  const profile = profiles[profileIndex];
  const value = await vscode.window.showInputBox({
    prompt: `Compile flags for ${typeof profile.compiler === "string" ? profile.compiler : "compiler"} ${typeof profile.ext === "string" ? profile.ext : ""}`.trim(),
    value: typeof profile.flags === "string" ? profile.flags : "",
    placeHolder: "-Wall -Wextra -Werror -MMD -MP"
  });
  if (value === undefined) {
    throw new Error("Compile flags update was cancelled.");
  }

  const originalProfiles = entry.compile_profiles;
  const actualIndex = originalProfiles.findIndex((candidate) => candidate === profile);
  if (actualIndex < 0) {
    throw new Error("Compile profile could not be updated.");
  }
  originalProfiles[actualIndex].flags = value.trim();
  saveConfigEntries(workspaceFolder, entries);
}

async function updateLinkFlags(workspaceFolder, entryIndex) {
  const entries = getConfigEntries(workspaceFolder);
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
  saveConfigEntries(workspaceFolder, entries);
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

function getProgramDescription(entry) {
  const binName = typeof entry.bin_name === "string" ? entry.bin_name : "";
  const runArgs = getRunArgsDescription(entry);
  if (!binName) {
    return runArgs;
  }
  return `${binName} | ${runArgs}`;
}

function getRunArgsDescription(entry) {
  return typeof entry.run_args === "string" && entry.run_args ? entry.run_args : "No args";
}

function getCompileFlagsSummary(entry) {
  const profiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles.filter(isObject) : [];
  if (profiles.length === 0) {
    return "No compile profiles";
  }
  return profiles
    .map((profile) => {
      const compiler = typeof profile.compiler === "string" ? profile.compiler : "compiler";
      const ext = typeof profile.ext === "string" ? profile.ext : "";
      return `${compiler} ${ext}`.trim();
    })
    .join(", ");
}

function isObject(value) {
  return Boolean(value) && typeof value === "object";
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

module.exports = {
  activate,
  deactivate
};
