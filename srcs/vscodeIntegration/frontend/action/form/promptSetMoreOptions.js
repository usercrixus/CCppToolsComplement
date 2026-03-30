const { showFormBox } = require("../../graphic/boxes/formBox");

async function promptSetMoreOptions(currentHiddenSuffixes = "", currentForceCamelCase = "off") {
  return showFormBox({
    panelType: "ccppToolsComplement.fakeCamelCaseOptionsForm",
    title: "Fake camel case options",
    description: "Choose which suffixes should be hidden and whether camel case should be forced.",
    fields: [
      {
        name: "hiddenSuffixes",
        label: "Suffixes to hide",
        type: "text",
        presetValue: currentHiddenSuffixes,
        placeholder: ".c .o .txt",
        regexValidator: "^\\s*(?:\\.[^\\s.]+(?:\\s+\\.[^\\s.]+)*)?\\s*$",
        regexErrorMessage: "Use a space-separated list like .c .o .txt",
        helpText: "Space-separated suffix list."
      },
      {
        name: "forceCamelCase",
        label: "Would you force camel case",
        type: "text",
        presetValue: currentForceCamelCase,
        placeholder: "on or off",
        regexValidator: "^(?i:(on|off))$",
        regexErrorMessage: "Use on or off.",
        helpText: "Enter on or off."
      }
    ]
  });
}

module.exports = {
  promptSetMoreOptions
};
