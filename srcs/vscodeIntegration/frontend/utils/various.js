const fs = require("fs");
const path = require("path");
const globals = require("../globals");
const { verifyJson } = require("../bridge");

const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read JSON file '${filePath}'.`);
  }
}

function getPathFromWorkspace(relativePath) {
  return path.join(globals.workspaceFolder.uri.fsPath, relativePath);
}

async function getMakefileConfigJson() {
  const configPath = getPathFromWorkspace(CONFIG_REL_PATH);
  if (!fs.existsSync(configPath)) {
    return [];
  }
  const status = await verifyJson([], false);
  if (status !== 0) {
    throw new Error(`Config file '${configPath}' contain errors.`);
  }
  return readJsonFile(configPath);
}

function getProgramNameFromEntry(entry) {
  const outputMakefile = typeof entry.output_makefile === "string" ? entry.output_makefile : "";
  const prefix = "Makefile.";
  const name = path.basename(outputMakefile);
  if (name.startsWith(prefix)) {
    const programName = name.slice(prefix.length).trim();
    if (programName && !programName.includes(".")) {
      return programName;
    }
  }
  return outputMakefile || "Unnamed program";
}

function getLaunchConfiguration(configurationName) {
  const launchPath = path.join(globals.workspaceFolder.uri.fsPath, LAUNCH_REL_PATH);
  const launchJson = readJsonFile(launchPath);
  const configurations = Array.isArray(launchJson.configurations) ? launchJson.configurations : [];
  const configuration = configurations.find((item) => item && item.name === configurationName);
  if (!configuration) {
    throw new Error(`Launch configuration '${configurationName}' was not generated.`);
  }
  return configuration;
}

module.exports = {
  getMakefileConfigJson,
  readJsonFile,
  getProgramNameFromEntry,
  getLaunchConfiguration
};
