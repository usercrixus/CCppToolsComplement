const vscode = require("vscode");
const { getWorkspaceFolder, getExtentionAbsolutePath } = require("./utilsVsCode");
const { createLaunch } = require("./bridge");
const { CREATE_LAUNCH_ACTION, pickProgram, handleProgramActions } = require("./graphic");

const COMMAND_ID = "ccppToolsComplement.generateAndDebugFromCurrentFile";
const BACKEND_PYTHON_ROOT = "backend";
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

function deactivate() { }

async function generateAndDebugFromCurrentFile() {
  const workspaceFolder = getWorkspaceFolder();
  const pythonBin = vscode.workspace.getConfiguration("ccppToolsComplement").get("pythonPath", "python3");
  const pythonPathRoot = getExtentionAbsolutePath(extensionContext, BACKEND_PYTHON_ROOT);

  while (true) {
    const selection = await pickProgram(workspaceFolder, pythonBin, pythonPathRoot);
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

module.exports = {
  activate,
  deactivate
};
