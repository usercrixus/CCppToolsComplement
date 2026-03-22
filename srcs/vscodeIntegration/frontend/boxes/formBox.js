const vscode = require("vscode");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function sanitizeField(field, index) {
  const name = typeof field?.name === "string" && field.name.trim()
    ? field.name.trim()
    : `field_${index}`;
  const type = field?.type === "textarea" ? "textarea" : "text";
  return {
    name,
    label: typeof field?.label === "string" && field.label.trim() ? field.label.trim() : name,
    type,
    presetValue: typeof field?.presetValue === "string" ? field.presetValue : "",
    regexValidator: typeof field?.regexValidator === "string" ? field.regexValidator : "",
    placeholder: typeof field?.placeholder === "string" ? field.placeholder : "",
    required: Boolean(field?.required),
    helpText: typeof field?.helpText === "string" ? field.helpText : ""
  };
}

function buildFormHtml(title, description, fields) {
  const serializedFields = JSON.stringify(fields).replace(/</g, "\\u003c");
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escapeHtml(title)}</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: var(--vscode-editor-background);
      --fg: var(--vscode-editor-foreground);
      --muted: var(--vscode-descriptionForeground);
      --border: var(--vscode-panel-border);
      --input-bg: var(--vscode-input-background);
      --input-fg: var(--vscode-input-foreground);
      --input-border: var(--vscode-input-border);
      --button-bg: var(--vscode-button-background);
      --button-fg: var(--vscode-button-foreground);
      --button-hover: var(--vscode-button-hoverBackground);
      --secondary-bg: var(--vscode-button-secondaryBackground);
      --secondary-fg: var(--vscode-button-secondaryForeground);
      --danger: #d14d41;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        radial-gradient(circle at top, color-mix(in srgb, var(--bg) 88%, transparent), var(--bg));
      color: var(--fg);
      font: 15px/1.5 Georgia, "Times New Roman", serif;
    }

    .shell {
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 32px;
    }

    .panel {
      width: min(760px, 100%);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 24px;
      background: color-mix(in srgb, var(--bg) 94%, black 6%);
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
    }

    h1 {
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.1;
    }

    .lead {
      margin: 0 0 22px;
      color: var(--muted);
    }

    form {
      display: grid;
      gap: 18px;
    }

    .field {
      display: grid;
      gap: 8px;
    }

    label {
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.01em;
    }

    input, textarea {
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--input-border);
      background: var(--input-bg);
      color: var(--input-fg);
      padding: 14px 16px;
      font: 14px/1.5 Consolas, "Liberation Mono", monospace;
    }

    textarea {
      min-height: 180px;
      resize: vertical;
    }

    .help {
      margin: 0;
      color: var(--muted);
      font-size: 12px;
    }

    .error {
      min-height: 18px;
      color: var(--danger);
      font-size: 12px;
    }

    .actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      margin-top: 4px;
    }

    button {
      border: 0;
      border-radius: 999px;
      padding: 10px 18px;
      cursor: pointer;
      font: inherit;
    }

    .secondary {
      background: var(--secondary-bg);
      color: var(--secondary-fg);
    }

    .primary {
      background: var(--button-bg);
      color: var(--button-fg);
    }

    .primary:hover { background: var(--button-hover); }
  </style>
</head>
<body>
  <div class="shell">
    <div class="panel">
      <h1>${escapeHtml(title)}</h1>
      <p class="lead">${escapeHtml(description)}</p>
      <form id="form"></form>
      <div class="actions">
        <button class="secondary" id="cancel" type="button">Cancel</button>
        <button class="primary" id="save" type="button">Save</button>
      </div>
    </div>
  </div>
  <script>
    const vscode = acquireVsCodeApi();
    const fields = ${serializedFields};
    const form = document.getElementById("form");
    const save = document.getElementById("save");
    const cancel = document.getElementById("cancel");

    function createField(field) {
      const wrapper = document.createElement("div");
      wrapper.className = "field";

      const label = document.createElement("label");
      label.htmlFor = field.name;
      label.textContent = field.label;
      wrapper.appendChild(label);

      const input = document.createElement(field.type === "textarea" ? "textarea" : "input");
      input.id = field.name;
      input.name = field.name;
      input.value = field.presetValue;
      input.placeholder = field.placeholder || "";
      if (field.type !== "textarea") {
        input.type = field.type;
      }
      wrapper.appendChild(input);

      if (field.helpText) {
        const help = document.createElement("p");
        help.className = "help";
        help.textContent = field.helpText;
        wrapper.appendChild(help);
      }

      const error = document.createElement("div");
      error.className = "error";
      error.id = field.name + "__error";
      wrapper.appendChild(error);

      return wrapper;
    }

    function validateField(field) {
      const input = document.getElementById(field.name);
      const error = document.getElementById(field.name + "__error");
      const value = input.value;
      error.textContent = "";

      if (field.required && !value) {
        error.textContent = "This field is required.";
        return false;
      }

      if (field.regexValidator) {
        try {
          const regex = new RegExp(field.regexValidator);
          if (value && !regex.test(value)) {
            error.textContent = "Value does not match the required format.";
            return false;
          }
        } catch (_error) {
          error.textContent = "Invalid field validator.";
          return false;
        }
      }

      return true;
    }

    function validateForm() {
      let isValid = true;
      for (const field of fields) {
        if (!validateField(field)) {
          isValid = false;
        }
      }
      return isValid;
    }

    function collectValues() {
      const values = {};
      for (const field of fields) {
        values[field.name] = document.getElementById(field.name).value;
      }
      return values;
    }

    for (const field of fields) {
      const node = createField(field);
      form.appendChild(node);
      const input = node.querySelector("input, textarea");
      input.addEventListener("input", () => validateField(field));
    }

    const firstInput = form.querySelector("input, textarea");
    if (firstInput) {
      firstInput.focus();
      firstInput.setSelectionRange?.(0, firstInput.value.length);
    }

    save.addEventListener("click", () => {
      if (!validateForm()) {
        return;
      }
      vscode.postMessage({ type: "submit", values: collectValues() });
    });

    cancel.addEventListener("click", () => {
      vscode.postMessage({ type: "cancel" });
    });

    window.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
        event.preventDefault();
        save.click();
      }
      if (event.key === "Escape") {
        event.preventDefault();
        cancel.click();
      }
    });
  </script>
</body>
</html>`;
}

function showFormBox({ panelType, title, description = "", fields }) {
  const normalizedFields = Array.isArray(fields) ? fields.map(sanitizeField) : [];
  return new Promise((resolve) => {
    const panel = vscode.window.createWebviewPanel(
      panelType,
      title,
      vscode.ViewColumn.Active,
      {
        enableScripts: true,
        retainContextWhenHidden: false
      }
    );

    let settled = false;
    const settle = (result) => {
      if (settled) {
        return;
      }
      settled = true;
      messageDisposable.dispose();
      disposeDisposable.dispose();
      panel.dispose();
      resolve(result);
    };

    panel.webview.html = buildFormHtml(title, description, normalizedFields);

    const messageDisposable = panel.webview.onDidReceiveMessage((message) => {
      if (!message || typeof message !== "object") {
        return;
      }
      if (message.type === "submit" && message.values && typeof message.values === "object") {
        settle(message.values);
      } else if (message.type === "cancel") {
        settle(undefined);
      }
    });

    const disposeDisposable = panel.onDidDispose(() => {
      settle(undefined);
    });
  });
}

module.exports = {
  showFormBox
};
