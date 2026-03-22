/**
 * @typedef {import("../shared/prototype").CompileProfile} CompileProfile
 * @typedef {import("../shared/prototype").MakefileConfigEntry} MakefileConfigEntry
 */

const { getMakefileConfigJson } = require("./utilsJson");
const {
    createLaunch,
    launchProgram,
    updateRunArgs,
    updateCompileFlagsForProfile,
    updateLinkFlags,
    deleteEntry
} = require("./action");
const { getProgramNameFromEntry } = require("./utilsOthers");

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

/**
 * @param {MakefileConfigEntry} makefileJsonObject
 * @param {number} entryIndex
 * @param {import("vscode").WorkspaceFolder} workspaceFolder
 * @param {string} pythonBin
 * @param {string} pythonPathRoot
 * @returns {MenuNode[]}
 */
function createSubAction(makefileJsonObject, entryIndex, workspaceFolder, pythonBin, pythonPathRoot) {
    const runArgsDescription =
        typeof makefileJsonObject.run_args === "string" && makefileJsonObject.run_args
            ? makefileJsonObject.run_args
            : "No args";
    const linkFlagsDescription =
        typeof makefileJsonObject.link_flags === "string" && makefileJsonObject.link_flags
            ? makefileJsonObject.link_flags
            : "(empty)";
    const compileProfiles = Array.isArray(makefileJsonObject.compile_profiles)
        ? makefileJsonObject.compile_profiles
        : [];

    return [
        new MenuNode(
            "Launch program",
            "Build if needed and start the debugger",
            launchProgram,
            [workspaceFolder, makefileJsonObject, pythonBin, pythonPathRoot],
            []
        ),
        new MenuNode(
            "Set args",
            runArgsDescription,
            updateRunArgs,
            [workspaceFolder, entryIndex, pythonBin, pythonPathRoot],
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
                [workspaceFolder, entryIndex, profileIndex, pythonBin, pythonPathRoot],
                []
            ))
        ),
        new MenuNode(
            "Set link flags",
            linkFlagsDescription,
            updateLinkFlags,
            [workspaceFolder, entryIndex, pythonBin, pythonPathRoot],
            []
        ),
        new MenuNode(
            "Delete entry",
            "Remove this program entry from makefileConfig.json",
            deleteEntry,
            [workspaceFolder, entryIndex, pythonBin, pythonPathRoot],
            []
        )
    ]
}

/**
 * @param {MakefileConfigEntry[]} makefileJsonObject
 * @param {import("vscode").WorkspaceFolder} workspaceFolder
 * @param {string} pythonBin
 * @param {string} pythonPathRoot
 * @returns {MenuNode[]}
 */
function createAction(makefileJsonObject, workspaceFolder, pythonBin, pythonPathRoot) {
    const menuAction = []
    for (const [entryIndex, entry] of makefileJsonObject.entries()) {
        menuAction.push(new MenuNode(
            getProgramNameFromEntry(entry),
            "Options for: " + getProgramNameFromEntry(entry),
            null,
            [],
            createSubAction(entry, entryIndex, workspaceFolder, pythonBin, pythonPathRoot)
        ))
    }
    return menuAction;
}

/**
 * @param {import("vscode").WorkspaceFolder} workspaceFolder
 * @param {string} pythonBin
 * @param {string} pythonPathRoot
 */
async function createMenu(workspaceFolder, pythonBin, pythonPathRoot) {
    /** @type {MakefileConfigEntry[]} */
    const makefileConfigJson = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot);
    const menu = createAction(makefileConfigJson, workspaceFolder, pythonBin, pythonPathRoot);
    menu.push(
        new MenuNode(
            "Create new launch",
            "Add a new program entry and regenerate VS Code launch.json",
            createLaunch,
            [workspaceFolder, pythonBin, pythonPathRoot],
            []
        )
    );
    return menu;
}

module.exports = {
    createMenu,
};
