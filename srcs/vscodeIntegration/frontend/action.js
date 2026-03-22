const path = require("path");
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

function normalizeConfigPath(filePath) {
  return filePath.split(path.sep).join("/");
}

function resolveGenerateJsonOutputPath(workspaceFolder, mainPathInput, programName, outputPathInput) {
  if (typeof outputPathInput === "string" && outputPathInput.trim()) {
    const explicitOutputPath = outputPathInput.trim();
    return path.isAbsolute(explicitOutputPath)
      ? explicitOutputPath
      : path.resolve(workspaceFolder.uri.fsPath, explicitOutputPath);
  }
  const resolvedMainPath = path.isAbsolute(mainPathInput)
    ? mainPathInput
    : path.resolve(workspaceFolder.uri.fsPath, mainPathInput);
  return path.resolve(path.dirname(resolvedMainPath), `Makefile.${programName}`);
}

function getGenerateJsonModuleArgs(workspaceFolder, values) {
  const mainPath = values.mainPath.trim();
  const programName = values.programName.trim();
  const runArgs = values.runArgs ?? "";
  const binName = values.binName ?? "";
  const outputPath = values.outputPath ?? "";
  const moduleArgs = [
    "--main-path",
    mainPath,
    "--program-name",
    programName
  ];
  if (runArgs) {
    moduleArgs.push("--run-args", runArgs);
  }
  if (binName) {
    moduleArgs.push("--bin-name", binName);
  }
  if (outputPath) {
    moduleArgs.push("--output-path", outputPath);
  }
  return moduleArgs;
}

function findEntryIndexByOutputMakefile(entries, outputMakefile) {
  return entries.findIndex((entry) => entry?.output_makefile === outputMakefile);
}

async function promptGenerateJsonArgs() {
  return showFormBox({
    panelType: "ccppToolsComplement.createLaunchForm",
    title: "Create launch entry",
    description: "Provide the data needed to create one makefileConfig.json entry.",
    fields: [
      {
        name: "mainPath",
        label: "Main path",
        type: "text",
        presetValue: "",
        regexValidator: "^.+$",
        required: true,
        helpText: "Relative to the workspace or absolute path to the main source file."
      },
      {
        name: "programName",
        label: "Program name",
        type: "text",
        presetValue: "",
        regexValidator: "^.+$",
        required: true,
        helpText: "Used in the Makefile name: Makefile.<program>."
      },
      {
        name: "runArgs",
        label: "Run arguments",
        type: "textarea",
        presetValue: "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact argument string forwarded to the generated launch configuration."
      },
      {
        name: "binName",
        label: "Binary name",
        type: "text",
        presetValue: "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Leave empty to use <program>.out."
      },
      {
        name: "outputPath",
        label: "Output Makefile path",
        type: "text",
        presetValue: "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Leave empty to use the main file directory with Makefile.<program>."
      }
    ]
  });
}

async function promptFlagsForEntry(entry) {
  const compileProfiles = Array.isArray(entry?.compile_profiles) ? entry.compile_profiles : [];
  return showFormBox({
    panelType: "ccppToolsComplement.createLaunchFlagsForm",
    title: "Set build flags",
    description: "Provide linker flags and compile flags for each detected profile.",
    fields: [
      {
        name: "linkFlags",
        label: `Link flags (${entry.link_compiler})`,
        type: "textarea",
        presetValue: typeof entry.link_flags === "string" ? entry.link_flags : "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact linker flags string."
      },
      ...compileProfiles.map((profile, profileIndex) => ({
        name: `compileFlags_${profileIndex}`,
        label: `${profile.compiler} ${profile.ext}`.trim(),
        type: "textarea",
        presetValue: typeof profile.flags === "string" ? profile.flags : "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact compile flags string for this profile."
      }))
    ]
  });
}

async function createLaunch(args) {
  const [workspaceFolder, pythonBin, pythonPathRoot] = args;
  const values = await promptGenerateJsonArgs();
  if (values === undefined) {
    return false;
  }

  const moduleArgs = getGenerateJsonModuleArgs(workspaceFolder, values);
  await generateJson([workspaceFolder, moduleArgs, pythonBin, pythonPathRoot]);

  const resolvedOutputPath = resolveGenerateJsonOutputPath(
    workspaceFolder,
    values.mainPath.trim(),
    values.programName.trim(),
    values.outputPath ?? ""
  );
  const outputMakefile = normalizeConfigPath(
    path.relative(workspaceFolder.uri.fsPath, resolvedOutputPath)
  );
  const entries = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
  const entryIndex = findEntryIndexByOutputMakefile(entries, outputMakefile);
  if (entryIndex < 0) {
    throw new Error(`Created entry '${outputMakefile}' was not found in makefileConfig.json.`);
  }

  const flagsValues = await promptFlagsForEntry(entries[entryIndex]);
  if (flagsValues === undefined) {
    return false;
  }

  await updateLinkFlagsHelper([
    workspaceFolder,
    entryIndex,
    flagsValues.linkFlags ?? "",
    pythonBin,
    pythonPathRoot
  ]);

  const compileProfiles = Array.isArray(entries[entryIndex].compile_profiles)
    ? entries[entryIndex].compile_profiles
    : [];
  for (const [profileIndex] of compileProfiles.entries()) {
    await updateCompileFlagsForProfileHelper([
      workspaceFolder,
      entryIndex,
      profileIndex,
      flagsValues[`compileFlags_${profileIndex}`] ?? "",
      pythonBin,
      pythonPathRoot
    ]);
  }

  await regenerateLaunchFiles([workspaceFolder, pythonBin, pythonPathRoot], true);
  return true;
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
  const [workspaceFolder, , pythonBin, pythonPathRoot] = args;
  await deleteEntryHelper(args);
  await deleteAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
  await generateAllMakefiles([workspaceFolder, pythonBin, pythonPathRoot]);
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
