const Module = require("module");
const path = require("path");

const makefileConfigJson = [
    {
        output_makefile: "Makefile.demo",
        run_args: "",
        link_flags: "",
        compile_profiles: [
            {
                compiler: "g++",
                ext: ".cpp",
                flags: "-O2 -g"
            }
        ]
    }
];

const originalLoad = Module._load;
Module._load = function patchedLoad(request, parent, isMain) {
    if (request === "./utilsJson" && parent && parent.filename.endsWith(path.join("frontend", "menuAsJson.js"))) {
        return {
            getMakefileConfigJson: async () => makefileConfigJson
        };
    }

    if (request === "./bridge" && parent && parent.filename.endsWith(path.join("frontend", "menuAsJson.js"))) {
        return {
            getProgramNameFromEntry: (entry) => {
                const outputMakefile = typeof entry.output_makefile === "string" ? entry.output_makefile : "";
                return outputMakefile.replace(/^.*Makefile\./, "") || "Unnamed program";
            }
        };
    }

    return originalLoad.call(this, request, parent, isMain);
};

const { createMenu } = require("../../srcs/vscodeIntegration/frontend/menuAsJson");

Module._load = originalLoad;

function printMenu(menu, indent = 0) {
    for (const entry of menu) {
        console.log(`${" ".repeat(indent)}- ${entry.label}: ${entry.description}`);
        if (Array.isArray(entry.sub) && entry.sub.length > 0) {
            printMenu(entry.sub, indent + 2);
        }
    }
}

async function main() {
    const menu = await createMenu({}, "python3", ".");
    printMenu(menu);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
