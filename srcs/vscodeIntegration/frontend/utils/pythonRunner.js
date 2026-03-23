const { execFile } = require("child_process");
const path = require("path");
const vscode = require("vscode");
const globals = require("../globals");

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
  moduleName,
  interactive,
  throwOnError = true,
  moduleArgs = []
) {
  const workspaceFolder = globals.workspaceFolder;
  const pythonBin = globals.pythonBin;
  const pythonPathRoot = globals.pythonPathRoot;
  if (!interactive) {
    const exitCode = await runPythonModuleProcess(
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

function runPythonModuleProcess(moduleName, moduleArgs) {
  const workspaceFolder = globals.workspaceFolder;
  const pythonBin = globals.pythonBin;
  const pythonPathRoot = globals.pythonPathRoot;
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
