const path = require("path");
const { readJsonFile } = require("./utilsJson");

const LAUNCH_REL_PATH = path.join(".vscode", "launch.json");

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

function getCompileProfileLabel(profile) {
  const compiler = typeof profile.compiler === "string" ? profile.compiler : "compiler";
  const ext = typeof profile.ext === "string" ? profile.ext : "";
  return `${compiler} ${ext}`.trim();
}

function getLaunchConfiguration(workspaceFolder, configurationName) {
  const launchPath = path.join(workspaceFolder.uri.fsPath, LAUNCH_REL_PATH);
  const launchJson = readJsonFile(launchPath);
  const configurations = Array.isArray(launchJson.configurations) ? launchJson.configurations : [];
  const configuration = configurations.find((item) => item && item.name === configurationName);
  if (!configuration) {
    throw new Error(`Launch configuration '${configurationName}' was not generated.`);
  }
  return configuration;
}

module.exports = {
  getProgramNameFromEntry,
  getLaunchConfiguration
};
