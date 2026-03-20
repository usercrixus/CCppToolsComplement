const vscode = require("vscode");
const { createMenu } = require("./menuAsJson");
const { launchProgram } = require("./bridge");

async function pickProgram(workspaceFolder, pythonBin, pythonPathRoot) {
  const menu = await createMenu(workspaceFolder, pythonBin, pythonPathRoot);
  await runMenu(menu);
}

async function runMenu(rootMenuNodes) {
  const menuStack = [
    {
      menuNodes: rootMenuNodes,
      placeHolder: "Select a program"
    }
  ];

  while (menuStack.length > 0) {
    const currentMenu = menuStack[menuStack.length - 1];
    const items = currentMenu.menuNodes.map((node) => ({
      label: node.label,
      description: node.description,
      node
    }));

    if (menuStack.length > 1) {
      items.push({
        label: "Back",
        description: "Return to the previous menu",
        node: null
      });
    }

    const selected = await pickQuickPickItem(items, currentMenu.placeHolder);

    if (!selected.node) {
      menuStack.pop();
      continue;
    }

    if (Array.isArray(selected.node.sub) && selected.node.sub.length > 0) {
      menuStack.push({
        menuNodes: selected.node.sub,
        placeHolder: selected.node.label
      });
      continue;
    }

    const shouldExitMenu = await executeMenuNode(selected.node);
    if (shouldExitMenu) {
      break;
    }
  }
}

async function executeMenuNode(node) {
  if (typeof node.runner !== "function") {
    return false;
  }

  await node.runner(node.args);
  return node.runner === launchProgram;
}

async function pickQuickPickItem(items, placeHolder) {
  const selected = await vscode.window.showQuickPick(items, {
    placeHolder
  });

  if (!selected) {
    throw new Error("Menu selection was cancelled.");
  }

  return selected;
}

module.exports = {
  pickProgram
};
