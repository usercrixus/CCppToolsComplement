const vscode = require("vscode");
const {
  generateJson,
  generateMakefile,
  generateVscodeIntegration,
  deleteEntryHelper,
  updateRunArgsHelper,
  updateCompileFlagsForProfileHelper,
  updateLinkFlagsHelper,
  deleteAllMakefiles
} = require("./bridge");
const { getMakefileConfigJson } = require("./utilsJson");
const { getProgramNameFromEntry, getLaunchConfiguration } = require("./utilsOthers");
const { showFormBox } = require("./boxes/formBox");

async function createLaunch(args) {
  await generateJson(args);
  await regenerateLaunchFiles(args, true);
}

async function launchProgram(args) {
  const [workspaceFolder, entry] = args;
  const launchConfig = getLaunchConfiguration(workspaceFolder, getProgramNameFromEntry(entry));
  const started = await vscode.debug.startDebugging(workspaceFolder, launchConfig);
  if (!started) {
    throw new Error("VSCode did not start the debugger.");
  }
  return true;
}

async function deleteEntry(args) {
  await deleteEntryHelper(args);
  await deleteAllMakefiles(args);
  await generateAllMakefiles(args);
}

async function generateAllMakefiles(args) {
  await generateMakefile(args);
}

async function regenerateLaunchFiles(args, regenerateMakefiles) {
  if (regenerateMakefiles) {
    await generateMakefile(args);
  }
  await generateVscodeIntegration(args);
}

async function updateRunArgs(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const currentRunArgs = entry.run_args;
  const values = await showFormBox({
    panelType: "ccppToolsComplement.runArgsForm",
    title: "Update run arguments",
    description: "Edit the argument string passed to the generated launch configuration.",
    fields: [
      {
        name: "runArgs",
        label: "Run arguments",
        type: "textarea",
        presetValue: currentRunArgs,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact argument string that should be forwarded to the program."
      }
    ]
  });
  if (values === undefined) {
    return false;
  }
  const newArgs = values.runArgs;
  await updateRunArgsHelper([workspaceFolder, entryIndex, newArgs, pythonBin, pythonPathRoot]);
  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
}

async function updateCompileFlagsForProfile(args) {
  const [workspaceFolder, entryIndex, profileIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const profile = entry.compile_profiles[profileIndex];
  const compiler = profile.compiler;
  const extension = profile.ext;
  const currentFlags = profile.flags;
  const values = await showFormBox({
    panelType: "ccppToolsComplement.compileFlagsForm",
    title: `Update compile flags`,
    description: `Edit the compile flags for ${compiler} ${extension}`.trim(),
    fields: [
      {
        name: "compileFlags",
        label: `${compiler} ${extension}`.trim(),
        type: "textarea",
        presetValue: currentFlags,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact compile flags string stored in makefileConfig.json."
      }
    ]
  });
  if (values === undefined) {
    return false;
  }
  const newFlags = values.compileFlags;
  await updateCompileFlagsForProfileHelper([
    workspaceFolder,
    entryIndex,
    profileIndex,
    newFlags,
    pythonBin,
    pythonPathRoot
  ]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  return true;
}

async function updateLinkFlags(args) {
  const [workspaceFolder, entryIndex, pythonBin, pythonPathRoot] = args;
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entry = entries[entryIndex];
  const currentLinkFlags = entry.link_flags;
  const linkCompiler = entry.link_compiler;
  const values = await showFormBox({
    panelType: "ccppToolsComplement.linkFlagsForm",
    title: "Update link flags",
    description: `Edit the link flags used by ${linkCompiler}.`,
    fields: [
      {
        name: "linkFlags",
        label: "Link flags",
        type: "textarea",
        presetValue: currentLinkFlags,
        regexValidator: "^[\\s\\S]*$",
        helpText: "Use the exact linker flags string stored in makefileConfig.json."
      }
    ]
  });
  if (values === undefined) {
    return false;
  }
  const newFlags = values.linkFlags;
  await updateLinkFlagsHelper([workspaceFolder, entryIndex, newFlags, pythonBin, pythonPathRoot]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  return true;
}

module.exports = {
  createLaunch,
  launchProgram,
  deleteEntry,
  updateRunArgs,
  updateCompileFlagsForProfile,
  updateLinkFlags
};
