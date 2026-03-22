const { execFile } = require("child_process");
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

async function runPythonModuleTask(
  workspaceFolder,
  pythonBin,
  pythonPathRoot,
  moduleName,
  interactive,
  throwOnError = true,
  moduleArgs = []
) {
  if (!interactive) {
    const exitCode = await runPythonModuleProcess(
      workspaceFolder,
      pythonBin,
      pythonPathRoot,
      moduleName,
      moduleArgs
    );
    if (throwOnError && exitCode !== 0) {
      throw new Error(`Task '${moduleName}' failed with exit code ${exitCode}.`);
    }
    return exitCode;
  }

  const task = new vscode.Task(
    { type: "shell" },
    workspaceFolder,
    `CCppToolsComplement: ${moduleName}`,
    "CCppToolsComplement",
    new vscode.ShellExecution(pythonBin, ["-m", moduleName, ...moduleArgs], {
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
  if (throwOnError && exitCode !== 0) {
    throw new Error(`Task '${moduleName}' failed with exit code ${exitCode}.`);
  }
  return exitCode;
}

function runPythonModuleProcess(workspaceFolder, pythonBin, pythonPathRoot, moduleName, moduleArgs) {
  return new Promise((resolve, reject) => {
    execFile(
      pythonBin,
      ["-m", moduleName, ...moduleArgs],
      {
        cwd: workspaceFolder.uri.fsPath,
        env: getPythonEnvironment(pythonPathRoot)
      },
      (error, stdout, stderr) => {
        if (!error) {
          resolve(0);
          return;
        }
        if (typeof stdout === "string" && stdout.trim()) {
          console.log(stdout.trim());
        }
        if (typeof stderr === "string" && stderr.trim()) {
          console.error(stderr.trim());
        }
        if (typeof error.code === "number") {
          resolve(error.code);
          return;
        }
        reject(error);
      }
    );
  });
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
