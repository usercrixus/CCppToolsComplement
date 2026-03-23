/**
 * @typedef {import("../../../shared/prototype").CompileProfile} CompileProfile
 * @typedef {import("../../../shared/prototype").MakefileConfigEntry} MakefileConfigEntry
 */

const { getMakefileConfigJson, getProgramNameFromEntry } = require("../../utils/various");
const { createLaunch } = require("../../action/createLaunch");
const { launchProgram } = require("../../action/launchProgram");
const { updateRunArgs } = require("../../action/updateRunArgs");
const { updateCompileFlagsForProfile } = require("../../action/updateCompileFlagsForProfile");
const { updateLinkFlags } = require("../../action/updateLinkFlags");
const { deleteEntry } = require("../../action/deleteEntry");

class MenuNode {
  constructor(label, description, runner = null, args = [], sub = []) {
    if (runner && sub.length > 0) {
      throw new Error("A menu entry cannot define both a runner and a submenu.");
    }
    this.label = label;
    this.description = description;
    this.runner = runner;
    this.args = args;
    this.sub = sub;
  }
}

function createSubAction(entry, entryIndex) {
  const runArgsDescription =
    typeof entry.run_args === "string" && entry.run_args
      ? entry.run_args
      : "No args";
  const linkFlagsDescription =
    typeof entry.link_flags === "string" && entry.link_flags
      ? entry.link_flags
      : "(empty)";
  const compileProfiles = Array.isArray(entry.compile_profiles)
    ? entry.compile_profiles
    : [];

  return [
    new MenuNode(
      "Launch program",
      "Build if needed and start the debugger",
      launchProgram,
      [entryIndex],
      []
    ),
    new MenuNode(
      "Set args",
      runArgsDescription,
      updateRunArgs,
      [entryIndex],
      []
    ),
    new MenuNode(
      "Set compile flags",
      compileProfiles.length > 0 ? "Select the compile profile to edit" : "No compile profiles",
      null,
      [],
      compileProfiles.map((compileProfile, profileIndex) => new MenuNode(
        `${compileProfile.compiler} ${compileProfile.ext}`.trim(),
        typeof compileProfile.flags === "string" && compileProfile.flags ? compileProfile.flags : "(empty)",
        updateCompileFlagsForProfile,
        [entryIndex, profileIndex],
        []
      ))
    ),
    new MenuNode(
      "Set link flags",
      linkFlagsDescription,
      updateLinkFlags,
      [entryIndex],
      []
    ),
    new MenuNode(
      "Delete entry",
      "Remove this program entry from makefileConfig.json",
      deleteEntry,
      [entryIndex],
      []
    )
  ];
}

function createAction(makefileJsonObject) {
  const menuAction = [];
  for (const [entryIndex, entry] of makefileJsonObject.entries()) {
    menuAction.push(new MenuNode(
      getProgramNameFromEntry(entry),
      "Options for: " + getProgramNameFromEntry(entry),
      null,
      [],
      createSubAction(entry, entryIndex)
    ));
  }
  return menuAction;
}

async function createMenu() {
  const makefileConfigJson = await getMakefileConfigJson();
  const menu = createAction(makefileConfigJson);
  menu.push(
    new MenuNode(
      "Create new launch",
      "Add a new program entry and regenerate VS Code launch.json",
      createLaunch,
      [],
      []
    )
  );
  return menu;
}

module.exports = {
  createMenu
};
