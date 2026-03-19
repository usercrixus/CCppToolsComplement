const fs = require("fs");
const path = require("path");
const { getPathFromWorkspace } = require("./utilsVsCode");
const { runPythonModuleTask } = require("./pythonRunner");

const CONFIG_REL_PATH = path.join(".vscode", "makefileConfig.json");
const PYTHON_MODULE_PREFIX = "srcs.script";

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Unable to read JSON file '${filePath}'.`);
  }
}

function writeJsonFile(filePath, value) {
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot) {
  const configPath = getPathFromWorkspace(CONFIG_REL_PATH);
  if (!fs.existsSync(configPath)) {
    return [];
  }
  const status = await runPythonModuleTask(
    workspaceFolder,
    pythonBin,
    pythonPathRoot,
    `${PYTHON_MODULE_PREFIX}.verifyJson`,
    false,
    false
  );
  if (status !== 0) {
    throw new Error(`Config file '${configPath}' contain errors.`);
  }
  return readJsonFile(configPath);
}

module.exports = {
  getMakefileConfigJson,
  readJsonFile,
  writeJsonFile
};
