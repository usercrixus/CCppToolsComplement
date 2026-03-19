/**
 * @typedef {import("../shared/prototype").CompileProfile} CompileProfile
 * @typedef {import("../shared/prototype").MakefileConfigEntry} MakefileConfigEntry
 */

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
            "Current run arguments",
            prototypeUpdateRunArgs,
            [],
            []
        ),
        new MenuNode(
            "Set compile flags",
            "Select the compile profile to edit",
            null,
            [],
            [
                new MenuNode(
                    "Compile profile",
                    "Current flags for this profile",
                    prototypeUpdateCompileFlagsForProfile,
                    [],
                    []
                )
            ]
        ),
        new MenuNode(
            "Set link flags",
            "Current link flags",
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
    for (const obj in makefileJsonObject) {
        new MenuNode(
            "Launch program",
            "Build if needed and start the debugger",
            prototypeLaunchProgram,
            [],
            createSubAction(makefileJsonObject[obj])
        )
    }
}

function createMenu() {
    /** @type {MakefileConfigEntry[]} */
    const makefileConfigJson = getMakefileConfigJson()
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
