const { updateLinkFlagsHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utils/various");
const { promptLinkFlags } = require("./form/promptLinkFlags");
const { generateAllMakefiles } = require("./utils");

async function updateLinkFlags(args) {
  const [entryIndex] = args;
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  const currentLinkFlags = entry.link_flags;
  const linkCompiler = entry.link_compiler;
  const values = await promptLinkFlags(linkCompiler, currentLinkFlags);
  if (values === undefined) {
    return false;
  }
  const newFlags = values.linkFlags;
  await updateLinkFlagsHelper(entryIndex, newFlags);
  await generateAllMakefiles();
  return true;
}

module.exports = {
  updateLinkFlags
};
