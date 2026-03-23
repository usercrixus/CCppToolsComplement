const { setRunArgsHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utils/various");
const { promptRunArgs } = require("./form/promptRunArgs");
const { regenerateLaunchFiles } = require("./utils");

async function updateRunArgs(args) {
  const [entryIndex] = args;
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  const currentRunArgs = entry.run_args;
  const values = await promptRunArgs(currentRunArgs);
  if (values === undefined) {
    return false;
  }
  const newArgs = values.runArgs;
  await setRunArgsHelper(entryIndex, newArgs);
  await regenerateLaunchFiles(true);
  return true;
}

module.exports = {
  updateRunArgs
};
