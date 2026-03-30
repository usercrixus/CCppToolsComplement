const vscode = require("vscode");
const { promptSetMoreOptions } = require("./form/promptSetMoreOptions");
const { setJsonSettingsFileExcludeHelper } = require("../bridge");
const { setEnabled, isEnabled } = require("../fakeCamelCase/controller");

function getCurrentHiddenSuffixes() {
  const filesExclude = vscode.workspace.getConfiguration().get("files.exclude", {});
  if (!filesExclude || typeof filesExclude !== "object") {
    return "";
  }

  const suffixes = Object.entries(filesExclude)
    .filter(([, isHidden]) => isHidden === true)
    .map(([pattern]) => {
      const match = /^\*\*\/\*(\.[^./\s]+)$/.exec(pattern);
      return match ? match[1] : null;
    })
    .filter((suffix) => typeof suffix === "string");

  return suffixes.join(" ");
}

function getCurrentForceCamelCase() {
  return isEnabled() ? "on" : "off";
}

function normalizeHiddenSuffixes(hiddenSuffixes) {
  if (typeof hiddenSuffixes !== "string") {
    return "";
  }
  return hiddenSuffixes.trim().replace(/\s+/g, " ");
}

function parseForceCamelCase(value) {
  const normalized = String(value).trim().toLowerCase();
  if (normalized === "on") {
    return true;
  }
  if (normalized === "off") {
    return false;
  }
  throw new Error("forceCamelCase must be 'on' or 'off'.");
}

async function setMoreOption() {
  const values = await promptSetMoreOptions(
    getCurrentHiddenSuffixes(),
    getCurrentForceCamelCase()
  );
  if (values === undefined) {
    return false;
  }
  const hiddenSuffixes = normalizeHiddenSuffixes(values.hiddenSuffixes);
  const forceCamelCase = parseForceCamelCase(values.forceCamelCase);
  await setJsonSettingsFileExcludeHelper(hiddenSuffixes);
  await setEnabled(forceCamelCase);
  vscode.window.showInformationMessage("More options saved for preview.");
  return true;
}

module.exports = {
  setMoreOption
};
