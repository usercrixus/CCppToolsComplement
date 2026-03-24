const { deleteEntryHelper, deleteAllMakefiles, deleteLaunch, deleteTask } = require("../bridge");
const { getMakefileConfigJson, getProgramNameFromEntry } = require("../utils/various");
const { generateAllMakefiles } = require("./utils");

async function deleteEntry(args) {
  const [entryIndex] = args;
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  const programName = getProgramNameFromEntry(entry);
  await deleteEntryHelper(entryIndex);
  await deleteTask(programName);
  await deleteLaunch(programName);
  await deleteAllMakefiles();
  await generateAllMakefiles();
}

module.exports = {
  deleteEntry
};
