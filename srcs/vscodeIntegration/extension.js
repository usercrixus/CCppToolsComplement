const fs = require("fs");
const path = require("path");
const vscode = require("vscode");

const COMMAND_ID = "ccppToolsComplement.generateAndDebugFromCurrentFile";
const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");

function activate(context) {
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
  const activeFile = getActiveFile(workspaceFolder);
  const pythonBin = vscode.workspace.getConfiguration("ccppToolsComplement").get("pythonPath", "python3");

  await runPythonModuleTask(workspaceFolder, pythonBin, "srcs.script.generateJson", true);
  await runPythonModuleTask(workspaceFolder, pythonBin, "srcs.script.generateMakefileFromJson", false);
  await runPythonModuleTask(workspaceFolder, pythonBin, "srcs.script.generateVscodeIntegrationFromJson", false);

  const entry = await pickProgramEntry(workspaceFolder, activeFile);
  const programName = getProgramNameFromMakefile(entry.output_makefile);
  if (!programName) {
    throw new Error(`Unable to infer program name from '${entry.output_makefile}'.`);
  }

  const launchConfig = getLaunchConfiguration(workspaceFolder, `Debug graph ${programName}`);
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
}

function getWorkspaceFolder() {
  const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  if (!folder) {
    throw new Error("Open the project as a VSCode workspace before using CCppToolsComplement.");
  }
  return folder;
}

function getActiveFile(workspaceFolder) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    throw new Error("Open a C or C++ file before launching the generator.");
  }
  const filePath = editor.document.uri.fsPath;
  const relativePath = path.relative(workspaceFolder.uri.fsPath, filePath);
  if (relativePath.startsWith("..") || path.isAbsolute(relativePath)) {
    throw new Error("The active file must be inside the current workspace.");
  }
  if (!["c", "cpp"].includes(editor.document.languageId)) {
    throw new Error("The active editor must be a C or C++ source file.");
  }
  return path.resolve(filePath);
}

async function runPythonModuleTask(workspaceFolder, pythonBin, moduleName, interactive) {
  const task = new vscode.Task(
    { type: "shell" },
    workspaceFolder,
    `CCppToolsComplement: ${moduleName}`,
    "CCppToolsComplement",
    new vscode.ShellExecution(pythonBin, ["-m", moduleName], {
      cwd: workspaceFolder.uri.fsPath
    })
  );

  task.presentationOptions = {
    reveal: vscode.TaskRevealKind.Always,
    focus: interactive,
    panel: vscode.TaskPanelKind.Dedicated,
    clear: false
  };
  task.problemMatchers = [];

  const execution = await vscode.tasks.executeTask(task);
  const exitCode = await waitForTaskExecution(execution);
  if (exitCode !== 0) {
    throw new Error(`Task '${moduleName}' failed with exit code ${exitCode}.`);
  }
}

function waitForTaskExecution(execution) {
  return new Promise((resolve) => {
    const disposable = vscode.tasks.onDidEndTaskProcess((event) => {
      if (event.execution !== execution) {
        return;
      }
      disposable.dispose();
      resolve(event.exitCode ?? 0);
    });
  });
}

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read JSON file '${filePath}'.`);
  }
}

async function pickProgramEntry(workspaceFolder, activeFile) {
  const configPath = path.join(workspaceFolder.uri.fsPath, CONFIG_REL_PATH);
  const config = readJsonFile(configPath);
  if (!Array.isArray(config) || config.length === 0) {
    throw new Error(`No entries found in '${configPath}'.`);
  }

  const mainMatches = [];
  const sourceMatches = [];
  for (const entry of config) {
    if (!entry || typeof entry !== "object") {
      continue;
    }
    const sources = getAbsoluteSources(entry);
    if (sources.length === 0) {
      continue;
    }
    if (samePath(sources[0], activeFile)) {
      mainMatches.push(entry);
      continue;
    }
    if (sources.some((source) => samePath(source, activeFile))) {
      sourceMatches.push(entry);
    }
  }

  if (mainMatches.length === 1) {
    return mainMatches[0];
  }
  if (mainMatches.length > 1) {
    return pickEntryFromQuickPick(mainMatches);
  }
  if (sourceMatches.length === 1) {
    return sourceMatches[0];
  }
  if (sourceMatches.length > 1) {
    return pickEntryFromQuickPick(sourceMatches);
  }
  return pickEntryFromQuickPick(config.filter((entry) => entry && typeof entry === "object"));
}

function getAbsoluteSources(entry) {
  if (typeof entry.output_makefile !== "string" || !Array.isArray(entry.rel_sources)) {
    return [];
  }
  const baseDir = path.dirname(entry.output_makefile);
  return entry.rel_sources
    .filter((value) => typeof value === "string" && value.length > 0)
    .map((relativeSource) => path.resolve(baseDir, relativeSource));
}

async function pickEntryFromQuickPick(entries) {
  const items = entries.map((entry) => {
    const outputMakefile = typeof entry.output_makefile === "string" ? entry.output_makefile : "";
    const programName = getProgramNameFromMakefile(outputMakefile) || outputMakefile;
    const firstSource = Array.isArray(entry.rel_sources) && entry.rel_sources.length > 0 ? entry.rel_sources[0] : "";
    return {
      label: programName,
      description: firstSource,
      entry
    };
  });

  const selected = await vscode.window.showQuickPick(items, {
    placeHolder: "Select the program to generate and debug"
  });
  if (!selected) {
    throw new Error("Program selection was cancelled.");
  }
  return selected.entry;
}

function getProgramNameFromMakefile(outputMakefile) {
  const prefix = "Makefile.";
  const name = path.basename(outputMakefile || "");
  if (!name.startsWith(prefix)) {
    return null;
  }
  const programName = name.slice(prefix.length).trim();
  if (!programName || programName.includes(".")) {
    return null;
  }
  return programName;
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

function samePath(left, right) {
  return path.normalize(left) === path.normalize(right);
}

module.exports = {
  activate,
  deactivate
};
