const vscode = require("vscode");
const { createMenu } = require("./menuAsJson");
const { launchProgram } = require("./action");

async function pickProgram(workspaceFolder, pythonBin, pythonPathRoot) {
  const loadMenu = () => createMenu(workspaceFolder, pythonBin, pythonPathRoot);
  await runMenu(loadMenu);
}

function getMenuItems(currentMenu, includeBack) {
  const items = currentMenu.menuNodes.map((node) => ({
    label: node.label,
    description: node.description,
    node
  }));
  if (includeBack) {
    items.push({
      label: "Back",
      description: "Return to the previous menu",
      node: null
    });
  }
  return items;
}

async function runMenu(loadMenu) {
  let menuStack = createMenuStack(await loadMenu());
  let shouldExitMenu = false;
  while (!shouldExitMenu && menuStack.length > 0) {
    const currentMenu = getCurrentMenu(menuStack);
    const items = getMenuItems(currentMenu, canGoBack(menuStack));
    const selected = await pickQuickPickItem(items, currentMenu.placeHolder);
    if (!selected.node) {
      goBack(menuStack);
    } else if (hasSubMenu(selected.node)) {
      openSubMenu(menuStack, selected.node);
    } else {
      const actionResult = await executeMenuNode(selected.node);
      if (actionResult.refreshMenu) {
        menuStack = createMenuStack(await loadMenu());
      }
      shouldExitMenu = actionResult.shouldExitMenu;
    }
  }
}

function createMenuStack(rootMenuNodes) {
  return [{
    menuNodes: rootMenuNodes,
    placeHolder: "Select a program"
  }];
}

function getCurrentMenu(menuStack) {
  return menuStack[menuStack.length - 1];
}

function canGoBack(menuStack) {
  return menuStack.length > 1;
}

function goBack(menuStack) {
  menuStack.pop();
}

function hasSubMenu(node) {
  return Array.isArray(node.sub) && node.sub.length > 0;
}

function openSubMenu(menuStack, node) {
  menuStack.push({
    menuNodes: node.sub,
    placeHolder: node.label
  });
}

async function executeMenuNode(node) {
  if (typeof node.runner !== "function") {
    return { shouldExitMenu: false, refreshMenu: false };
  }
  await node.runner(node.args);
  return {
    shouldExitMenu: node.runner === launchProgram,
    refreshMenu: node.runner !== launchProgram
  };
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
