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

function createSubAction(/* makefilejsonobject for this specific launch */) {
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

function createAction(/*the root makefilejsonobject*/) {
    for (obj in makefilejsonobject) {
        new MenuNode(
            "Launch program",
            "Build if needed and start the debugger",
            prototypeLaunchProgram,
            [],
            createSubAction()
        )
    }
}

function createMenu() {
    return [
        createAction(),
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
