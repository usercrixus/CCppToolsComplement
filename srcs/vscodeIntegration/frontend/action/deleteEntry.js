const { deleteEntryHelper, deleteLaunch, deleteMakefile, deleteTask } = require("../bridge");
const { getMakefileConfigJson, getProgramNameFromEntry } = require("../utils/various");

async function deleteEntry(args) {
  const [entryIndex] = args;
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  const programName = getProgramNameFromEntry(entry);
  await deleteMakefile(entryIndex);
  await deleteEntryHelper(entryIndex);
  await deleteTask(programName);
  await deleteLaunch(programName);
}

module.exports = {
  deleteEntry
};
