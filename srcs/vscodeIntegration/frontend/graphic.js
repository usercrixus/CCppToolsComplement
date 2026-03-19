const vscode = require("vscode");
const { getMakefileConfigJson } = require("./utilsJson");
const {
  launchProgram,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags,
  getProgramNameFromEntry,
  getCompileProfileLabel
} = require("./bridge");

const CREATE_LAUNCH_ACTION = "ccppToolsComplement.createLaunch";
const MENU_RESULT_BACK = Symbol("menuBack");
const MENU_RESULT_REFRESH = Symbol("menuRefresh");

const PROGRAM_ACTION_MENU = [
  {
    label: "Launch program",
    description: "Build if needed and start the debugger",
    run: async (context) => launchProgram(
      context.workspaceFolder,
      context.entry,
      context.pythonBin,
      context.pythonPathRoot
    )
  },
  {
    label: "Set args",
    description: (context) => getRunArgsDescription(context.entry),
    run: async (context) => {
      await updateRunArgs(context.workspaceFolder, context.entryIndex, context.pythonBin, context.pythonPathRoot);
      return MENU_RESULT_REFRESH;
    }
  },
  {
    label: "Set compile flags",
    description: (context) => getCompileFlagsSummary(context.entry),
    childPlaceHolder: (context) => `Select compile flags to edit for ${getProgramNameFromEntry(context.entry)}`,
    children: (context) => getCompileProfileMenu(context.entry)
  },
  {
    label: "Set link flags",
    description: (context) => getLinkFlagsDescription(context.entry),
    run: async (context) => {
      await updateLinkFlags(context.workspaceFolder, context.entryIndex, context.pythonBin, context.pythonPathRoot);
      return MENU_RESULT_REFRESH;
    }
  }
];

async function pickProgram(workspaceFolder, pythonBin, pythonPathRoot) {
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const items = entries.map((entry, index) => ({
    label: getProgramNameFromEntry(entry),
    description: getProgramDescription(entry),
    entryIndex: index
  }));
  items.push({
    label: "Create new launch",
    description: "Add a new program entry and regenerate VS Code launch.json",
    entryIndex: CREATE_LAUNCH_ACTION
  });

  const selected = await vscode.window.showQuickPick(items, {
    placeHolder: "Select a program"
  });
  if (!selected) {
    throw new Error("Program selection was cancelled.");
  }
  return selected.entryIndex;
}

async function handleProgramActions(workspaceFolder, entryIndex, pythonBin, pythonPathRoot) {
  while (true) {
    const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
    const entry = entries[entryIndex];
    if (!entry) {
      throw new Error("Selected program no longer exists in makefileConfig.json.");
    }

    const result = await runMenu(PROGRAM_ACTION_MENU, {
      workspaceFolder,
      entryIndex,
      pythonBin,
      pythonPathRoot,
      entry
    }, {
      placeHolder: `Select an action for ${getProgramNameFromEntry(entry)}`,
      includeBack: true,
      backLabel: "Back",
      backDescription: "Return to the program list"
    });
    if (result === MENU_RESULT_BACK) {
      return null;
    }
    if (result && result !== MENU_RESULT_REFRESH) {
      return result;
    }
  }
}

async function runMenu(menuNodes, context, options) {
  const resolvedItems = await Promise.all(menuNodes.map((node) => resolveMenuNode(node, context)));
  if (options.includeBack) {
    resolvedItems.push({
      label: options.backLabel,
      description: options.backDescription,
      run: async () => MENU_RESULT_BACK
    });
  }
  const selected = await pickMenuItem(resolvedItems, options.placeHolder);
  if (selected.children) {
    const childResult = await runMenu(selected.children, context, {
      placeHolder: selected.childPlaceHolder || selected.label,
      includeBack: true,
      backLabel: "Back",
      backDescription: "Return to the previous menu"
    });
    return childResult === MENU_RESULT_BACK ? MENU_RESULT_REFRESH : childResult;
  }
  return selected.run(context);
}

async function resolveMenuNode(node, context) {
  const resolvedNode = {
    label: resolveMenuValue(node.label, context),
    description: resolveMenuValue(node.description, context)
  };
  if (node.run) {
    resolvedNode.run = node.run;
  }
  if (node.children) {
    resolvedNode.children = typeof node.children === "function" ? await node.children(context) : node.children;
    resolvedNode.childPlaceHolder = resolveMenuValue(node.childPlaceHolder, context);
  }
  return resolvedNode;
}

function resolveMenuValue(value, context) {
  return typeof value === "function" ? value(context) : value;
}

function getProgramDescription(entry) {
  const binName = typeof entry.bin_name === "string" ? entry.bin_name : "";
  const runArgs = getRunArgsDescription(entry);
  if (!binName) {
    return runArgs;
  }
  return `${binName} | ${runArgs}`;
}

function getRunArgsDescription(entry) {
  return typeof entry.run_args === "string" && entry.run_args ? entry.run_args : "No args";
}

function getCompileFlagsSummary(entry) {
  const profiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles.filter(isObject) : [];
  if (profiles.length === 0) {
    return "No compile profiles";
  }
  return profiles
    .map((profile) => getCompileProfileLabel(profile))
    .join(", ");
}

function getLinkFlagsDescription(entry) {
  return typeof entry.link_flags === "string" && entry.link_flags ? entry.link_flags : "(empty)";
}

function getCompileProfileMenu(entry) {
  const profiles = Array.isArray(entry.compile_profiles) ? entry.compile_profiles.filter(isObject) : [];
  return profiles.map((profile, index) => ({
    label: getCompileProfileLabel(profile),
    description: getCompileProfileFlagsDescription(profile),
    run: async (context) => {
      await updateCompileFlagsForProfile(
        context.workspaceFolder,
        context.entryIndex,
        index,
        context.pythonBin,
        context.pythonPathRoot
      );
      return MENU_RESULT_REFRESH;
    }
  }));
}

function getCompileProfileFlagsDescription(profile) {
  return typeof profile.flags === "string" && profile.flags ? profile.flags : "(empty)";
}

function isObject(value) {
  return Boolean(value) && typeof value === "object";
}

async function pickMenuItem(items, placeHolder) {
  const selected = await vscode.window.showQuickPick(items, {
    placeHolder
  });
  if (!selected) {
    throw new Error("Menu selection was cancelled.");
  }
  return selected;
}

module.exports = {
  CREATE_LAUNCH_ACTION,
  pickProgram,
  handleProgramActions
};
