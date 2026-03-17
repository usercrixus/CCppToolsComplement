const path = require("path");
const vscode = require("vscode");

function getPythonEnvironment(pythonPathRoot) {
  const existingPythonPath = process.env.PYTHONPATH;
  return {
    ...process.env,
    PYTHONPATH: existingPythonPath
      ? `${pythonPathRoot}${path.delimiter}${existingPythonPath}`
      : pythonPathRoot
  };
}

async function runPythonModuleTask(workspaceFolder, pythonBin, pythonPathRoot, moduleName, interactive) {
  const task = new vscode.Task(
    { type: "shell" },
    workspaceFolder,
    `CCppToolsComplement: ${moduleName}`,
    "CCppToolsComplement",
    new vscode.ShellExecution(pythonBin, ["-m", moduleName], {
      cwd: workspaceFolder.uri.fsPath,
      env: getPythonEnvironment(pythonPathRoot)
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

module.exports = {
  runPythonModuleTask
};
