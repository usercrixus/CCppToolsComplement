const vscode = require("vscode");
const { setGlobals } = require("./globals");
const { createFakeCamelCaseController } = require("./fakeCamelCase/controller");
const { pickProgram } = require("./graphic/menu/menu");

function activate(context) {
  context.subscriptions.push(createFakeCamelCaseController());

  const disposable = vscode.commands.registerCommand("ccppToolsComplement.generateAndDebugFromCurrentFile", async () => {
    try {
      setGlobals(context);
      await pickProgram();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(message);
    }
  });
  context.subscriptions.push(disposable);
}

function deactivate() { }

module.exports = {
  activate,
  deactivate
};
