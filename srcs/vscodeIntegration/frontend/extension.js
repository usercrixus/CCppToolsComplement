const vscode = require("vscode");
const { setGlobals } = require("./globals");
const { createFakeCamelCaseController } = require("./fakeCamelCase/controller");
const { pickProgram, pickGearMenu } = require("./graphic/menu/menu");

function activate(context) {
  context.subscriptions.push(createFakeCamelCaseController());

  const generateAndDebugCommand = vscode.commands.registerCommand("ccppToolsComplement.generateAndDebugFromCurrentFile", async () => {
    try {
      setGlobals(context);
      await pickProgram();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(message);
    }
  });

  const previewGearIconCommand = vscode.commands.registerCommand("ccppToolsComplement.previewGearIcon", async () => {
    try {
      setGlobals(context);
      await pickGearMenu();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      vscode.window.showErrorMessage(message);
    }
  });

  context.subscriptions.push(generateAndDebugCommand, previewGearIconCommand);
}

function deactivate() { }

module.exports = {
  activate,
  deactivate
};
