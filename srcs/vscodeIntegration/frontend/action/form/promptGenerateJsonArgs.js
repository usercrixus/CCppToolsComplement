const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptGenerateJsonArgs() {
  return showFormBox({
    panelType: "ccppToolsComplement.createLaunchForm",
    title: "Create launch entry",
    description: "Provide the data needed to create one makefileConfig.json entry.",
    fields: [
      {
        name: "mainPath",
        label: "Main path",
        type: "text",
        presetValue: "",
        regexValidator: "^.+$",
        required: true,
        helpText: "Relative to the workspace or absolute path to the main source file."
      },
      {
        name: "programName",
        label: "Program name",
        type: "text",
        presetValue: "",
        regexValidator: "^.+$",
        required: true,
        helpText: "Used in the Makefile name: Makefile.<program>."
      },
      {
        name: "runArgs",
        label: "Run arguments",
        type: "textarea",
        presetValue: "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Exact argument string forwarded to the generated launch configuration."
      },
      {
        name: "binName",
        label: "Binary name",
        type: "text",
        presetValue: "",
        regexValidator: "^[\\s\\S]*$",
        helpText: "Leave empty to use <program>.out."
      }
    ]
  });
}

module.exports = {
  promptGenerateJsonArgs
};
