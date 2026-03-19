/**
 * @typedef {import("../shared/prototype").CompileProfile} CompileProfile
 * @typedef {import("../shared/prototype").MakefileConfigEntry} MakefileConfigEntry
 */

const { getMakefileConfigJson } = require("./utilsJson");

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
 * @returns {MenuNode[]}
 */
function createSubAction(makefileJsonObject) {
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
            prototypeLaunchProgram,
            [],
            []
        ),
        new MenuNode(
            "Set args",
            runArgsDescription,
            prototypeUpdateRunArgs,
            [],
            []
        ),
        new MenuNode(
            "Set compile flags",
            compileProfiles.length > 0 ? "Select the compile profile to edit" : "No compile profiles",
            null,
            [],
            compileProfiles.map((compileProfile) => new MenuNode(
                `${compileProfile.compiler} ${compileProfile.ext}`.trim(),
                typeof compileProfile.flags === "string" && compileProfile.flags ? compileProfile.flags : "(empty)",
                prototypeUpdateCompileFlagsForProfile,
                [],
                []
            ))
        ),
        new MenuNode(
            "Set link flags",
            linkFlagsDescription,
            prototypeUpdateLinkFlags,
            [],
            []
        )
    ]
}

/**
 * @param {MakefileConfigEntry[]} makefileJsonObject
 */
function createAction(makefileJsonObject) {
    for (const entry of makefileJsonObject) {
        new MenuNode(
            "Launch program",
            "Build if needed and start the debugger",
            prototypeLaunchProgram,
            [],
            createSubAction(entry)
        )
    }
}

/**
 * @param {import("vscode").WorkspaceFolder} workspaceFolder
 * @param {string} pythonBin
 * @param {string} pythonPathRoot
 */
async function createMenu(workspaceFolder, pythonBin, pythonPathRoot) {
    /** @type {MakefileConfigEntry[]} */
    const makefileConfigJson = await getMakefileConfigJson(workspaceFolder, pythonBin, pythonPathRoot)
    return [
        createAction(makefileConfigJson),
        new MenuNode(
            "Create new launch",
            "Add a new program entry and regenerate VS Code launch.json",
            null,
            [],
            []
        )
    ]
}

function prototypeLaunchProgram() { }
function prototypeUpdateRunArgs() { }
function prototypeUpdateCompileFlagsForProfile() { }
function prototypeUpdateLinkFlags() { }

module.exports = {
    MenuNode,
    PROGRAM_ACTION_MENU,
    PROGRAM_ACTION,
    prototypeLaunchProgram,
    prototypeUpdateRunArgs,
    prototypeUpdateCompileFlagsForProfile,
    prototypeUpdateLinkFlags
};
