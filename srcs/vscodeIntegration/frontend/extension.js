const vscode = require("vscode");
const { getWorkspaceFolder, getExtentionAbsolutePath } = require("./utilsVsCode");
const { pickProgram } = require("./graphic");

const COMMAND_ID = "ccppToolsComplement.generateAndDebugFromCurrentFile";
const BACKEND_PYTHON_ROOT = "backend";
let extensionContext = null;

function activate(context) {
  extensionContext = context;
  const disposable = vscode.commands.registerCommand(COMMAND_ID, async () => {
    try {
      await rooting();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(message);
    }
  });
  context.subscriptions.push(disposable);
}

function deactivate() { }

async function rooting() {
  const workspaceFolder = getWorkspaceFolder();
  const pythonBin = vscode.workspace.getConfiguration("ccppToolsComplement").get("pythonPath", "python3");
  const pythonPathRoot = getExtentionAbsolutePath(extensionContext, BACKEND_PYTHON_ROOT);
  await pickProgram(workspaceFolder, pythonBin, pythonPathRoot);
}

module.exports = {
  activate,
  deactivate
};
