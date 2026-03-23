const { updateCompileFlagsForProfileHelper } = require("../bridge");
const { getMakefileConfigJson } = require("../utils/various");
const { promptCompileFlagsForProfile } = require("./form/promptCompileFlagsForProfile");
const { generateAllMakefiles } = require("./utils");

async function updateCompileFlagsForProfile(args) {
  const [entryIndex, profileIndex] = args;
  const entries = await getMakefileConfigJson();
  const entry = entries[entryIndex];
  const profile = entry.compile_profiles[profileIndex];
  const compiler = profile.compiler;
  const extension = profile.ext;
  const currentFlags = profile.flags;
  const values = await promptCompileFlagsForProfile(compiler, extension, currentFlags);
  if (values === undefined) {
    return false;
  }
  const newFlags = values.compileFlags;
  await updateCompileFlagsForProfileHelper(entryIndex, profileIndex, newFlags);
  await generateAllMakefiles();
  return true;
}

module.exports = {
  updateCompileFlagsForProfile
};
