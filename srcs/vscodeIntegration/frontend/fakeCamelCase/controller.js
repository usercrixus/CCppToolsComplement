const vscode = require("vscode");
const { findFakeCamelCaseMatches } = require("./transform");

const SUPPORTED_LANGUAGES = new Set(["c", "cpp"]);
const UPDATE_DELAY_MS = 120;
const FUNCTION_COLOR = "#dcdcaa";
const VARIABLE_COLOR = "#9cdcfe";

function getFakeCamelCaseConfiguration() {
  return vscode.workspace.getConfiguration("ccppToolsComplement.fakeCamelCase");
}

async function setEnabled(enabled) {
  await getFakeCamelCaseConfiguration().update(
    "enabled",
    Boolean(enabled),
    vscode.ConfigurationTarget.Workspace
  );
}

function isEnabled() {
  return getFakeCamelCaseConfiguration().get("enabled", true);
}

function shouldForceEditorForeground() {
  return getFakeCamelCaseConfiguration().get("forceEditorForeground", false);
}

function getForcedColor() {
  const configuredColor = getFakeCamelCaseConfiguration().get("forcedColor", "");
  return typeof configuredColor === "string" ? configuredColor.trim() : "";
}

function isSupportedEditor(editor) {
  return Boolean(editor) && SUPPORTED_LANGUAGES.has(editor.document.languageId);
}

function createDecorationType() {
  return vscode.window.createTextEditorDecorationType({
    color: "transparent",
    rangeBehavior: vscode.DecorationRangeBehavior.ClosedClosed
  });
}

function getOverlayColor(match, visibleText) {
  const forcedColor = getForcedColor();
  if (forcedColor) {
    return forcedColor;
  }
  if (shouldForceEditorForeground()) {
    return new vscode.ThemeColor("editor.foreground");
  }

  const trailingText = visibleText.slice(match.index + match.source.length);
  return /^\s*\(/.test(trailingText) ? FUNCTION_COLOR : VARIABLE_COLOR;
}

function createDecoration(editor, startOffset, endOffset, sourceText, displayText, color) {
  const after = {
    contentText: displayText,
    margin: `0 0 0 -${sourceText.length}ch`,
    color
  };

  return {
    range: new vscode.Range(
      editor.document.positionAt(startOffset),
      editor.document.positionAt(endOffset)
    ),
    renderOptions: {
      after
    }
  };
}

function updateEditor(editor, decorationType) {
  if (!isSupportedEditor(editor) || !isEnabled()) {
    if (editor) {
      editor.setDecorations(decorationType, []);
    }
    return;
  }

  const decorations = [];
  for (const visibleRange of editor.visibleRanges) {
    const startOffset = editor.document.offsetAt(visibleRange.start);
    const endOffset = editor.document.offsetAt(visibleRange.end);
    const text = editor.document.getText(visibleRange);
    const matches = findFakeCamelCaseMatches(text);

    for (const match of matches) {
      const color = getOverlayColor(match, text);
      decorations.push(
        createDecoration(
          editor,
          startOffset + match.index,
          startOffset + match.index + match.source.length,
          match.source,
          match.display,
          color
        )
      );
    }
  }

  editor.setDecorations(decorationType, decorations);
}

function createFakeCamelCaseController() {
  const decorationType = createDecorationType();
  const timers = new Map();

  function scheduleUpdate(editor) {
    if (!editor) {
      return;
    }

    const key = editor.document.uri.toString();
    const previousTimer = timers.get(key);
    if (previousTimer) {
      clearTimeout(previousTimer);
    }

    const timer = setTimeout(() => {
      timers.delete(key);
      updateEditor(editor, decorationType);
    }, UPDATE_DELAY_MS);

    timers.set(key, timer);
  }

  function refreshVisibleEditors() {
    for (const editor of vscode.window.visibleTextEditors) {
      scheduleUpdate(editor);
    }
  }

  refreshVisibleEditors();

  const disposables = [
    decorationType,
    vscode.window.onDidChangeActiveTextEditor((editor) => scheduleUpdate(editor)),
    vscode.window.onDidChangeVisibleTextEditors((editors) => {
      for (const editor of editors) {
        scheduleUpdate(editor);
      }
    }),
    vscode.window.onDidChangeTextEditorVisibleRanges((event) => scheduleUpdate(event.textEditor)),
    vscode.workspace.onDidChangeTextDocument((event) => {
      const editor = vscode.window.visibleTextEditors.find((candidate) => candidate.document === event.document);
      scheduleUpdate(editor);
    }),
    vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration("ccppToolsComplement.fakeCamelCase")) {
        refreshVisibleEditors();
      }
    }),
    new vscode.Disposable(() => {
      for (const timer of timers.values()) {
        clearTimeout(timer);
      }
      timers.clear();
    })
  ];

  return vscode.Disposable.from(...disposables);
}

module.exports = {
  createFakeCamelCaseController,
  setEnabled,
  isEnabled
};
