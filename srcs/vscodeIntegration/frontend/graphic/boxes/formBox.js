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
    regexErrorMessage: typeof field?.regexErrorMessage === "string" ? field.regexErrorMessage : "",
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
      --accent: #ff4fa3;
      --accent-soft: rgba(255, 79, 163, 0.16);
      --accent-strong: #ff2a8a;
      --accent-ink: #2a0717;
      --focus-accent: #8f8f95;
      --focus-soft: rgba(143, 143, 149, 0.12);
      --button-bg: rgba(0, 0, 0, 0.72);
      --button-fg: #f5f5f5;
      --button-hover: rgba(0, 0, 0, 0.84);
      --secondary-bg: rgba(0, 0, 0, 0.62);
      --secondary-fg: #f5f5f5;
      --danger: #d14d41;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        radial-gradient(circle at top, rgba(255, 79, 163, 0.08), transparent 36%),
        radial-gradient(circle at bottom, rgba(255, 79, 163, 0.05), transparent 42%),
        var(--bg);
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
      border: 1px solid color-mix(in srgb, var(--border) 82%, rgba(255, 255, 255, 0.04) 18%);
      border-radius: 18px;
      padding: 24px;
      background:
        linear-gradient(180deg, rgba(255, 79, 163, 0.05), transparent 22%),
        color-mix(in srgb, var(--bg) 96%, black 4%);
      box-shadow:
        0 22px 60px rgba(0, 0, 0, 0.34),
        0 0 0 1px rgba(255, 79, 163, 0.05) inset;
    }

    h1 {
      margin: 0 0 4px;
      font-size: 28px;
      line-height: 1.1;
      color: #f5f5f5;
      text-shadow: 0 0 18px rgba(255, 79, 163, 0.08);
    }

    .lead {
      margin: 0 0 18px;
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
      color: #f5f5f5;
    }

    input, textarea {
      width: 100%;
      border-radius: 12px;
      border: 1px solid color-mix(in srgb, var(--input-border) 88%, rgba(255, 255, 255, 0.04) 12%);
      background: var(--input-bg);
      color: var(--input-fg);
      padding: 14px 16px;
      font: 14px/1.5 Consolas, "Liberation Mono", monospace;
      transition: border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease;
    }

    textarea {
      min-height: 180px;
      resize: vertical;
    }

    input:focus, textarea:focus {
      outline: none;
      border-color: color-mix(in srgb, var(--input-border) 88%, rgba(255, 255, 255, 0.04) 12%);
      box-shadow: none;
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
      transition: transform 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
    }

    .secondary {
      background: var(--secondary-bg);
      color: var(--secondary-fg);
      box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 0 0 1px rgba(0, 0, 0, 0.48);
    }

    .primary {
      background: var(--button-bg);
      color: var(--button-fg);
      font-weight: 700;
      box-shadow:
        0 0 0 1px rgba(255, 255, 255, 0.04) inset,
        0 0 0 1px rgba(0, 0, 0, 0.48);
    }

    .primary:hover,
    .secondary:hover {
      transform: translateY(-1px);
    }

    .primary:hover {
      background: var(--button-hover);
      box-shadow:
        0 0 16px rgba(143, 143, 149, 0.14),
        0 0 0 1px rgba(255, 255, 255, 0.06) inset;
    }

    .secondary:hover {
      background: rgba(0, 0, 0, 0.78);
      box-shadow:
        0 0 14px rgba(143, 143, 149, 0.12),
        0 0 0 1px rgba(255, 255, 255, 0.05) inset;
    }

    .primary:focus-visible,
    .secondary:focus-visible {
      outline: none;
      box-shadow:
        0 0 0 1px rgba(143, 143, 149, 0.34),
        0 0 12px rgba(143, 143, 149, 0.14);
    }
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
      label.textContent = field.label;
      label.htmlFor = field.name;
      wrapper.appendChild(label);

      const input = document.createElement(field.type === "textarea" ? "textarea" : "input");
      input.id = field.name;
      input.name = field.name;
      input.value = field.presetValue;
      input.placeholder = field.placeholder;
      if (field.required) {
        input.required = true;
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
      error.dataset.errorFor = field.name;
      wrapper.appendChild(error);

      return wrapper;
    }

    function validateField(field, value) {
      if (field.required && !value.trim()) {
        return "This field is required.";
      }
      if (field.regexValidator) {
        const regex = new RegExp(field.regexValidator);
        if (!regex.test(value)) {
          return field.regexErrorMessage || "Value does not match the expected format.";
        }
      }
      return "";
    }

    function validateForm() {
      let hasError = false;
      for (const field of fields) {
        const input = form.elements.namedItem(field.name);
        const errorNode = form.querySelector('[data-error-for="' + field.name + '"]');
        const message = validateField(field, input.value);
        errorNode.textContent = message;
        if (message) {
          hasError = true;
        }
      }
      return !hasError;
    }

    function collectValues() {
      const values = {};
      for (const field of fields) {
        values[field.name] = form.elements.namedItem(field.name).value;
      }
      return values;
    }

    for (const field of fields) {
      form.appendChild(createField(field));
    }

    save.addEventListener("click", () => {
      if (!validateForm()) {
        return;
      }
      vscode.postMessage({
        type: "submit",
        values: collectValues()
      });
    });

    cancel.addEventListener("click", () => {
      vscode.postMessage({ type: "cancel" });
    });
  </script>
</body>
</html>`;
}

async function showFormBox(options) {
  const panelType = typeof options?.panelType === "string" && options.panelType.trim()
    ? options.panelType.trim()
    : "ccppToolsComplement.formBox";
  const title = typeof options?.title === "string" && options.title.trim()
    ? options.title.trim()
    : "Form";
  const description = typeof options?.description === "string" ? options.description : "";
  const fields = Array.isArray(options?.fields)
    ? options.fields.map((field, index) => sanitizeField(field, index))
    : [];

  const panel = vscode.window.createWebviewPanel(
    panelType,
    title,
    vscode.ViewColumn.Active,
    {
      enableScripts: true,
      retainContextWhenHidden: false
    }
  );

  panel.webview.html = buildFormHtml(title, description, fields);

  return new Promise((resolve) => {
    let settled = false;

    const finalize = (value) => {
      if (settled) {
        return;
      }
      settled = true;
      panel.dispose();
      resolve(value);
    };

    const messageDisposable = panel.webview.onDidReceiveMessage((message) => {
      if (message?.type === "submit" && message.values && typeof message.values === "object") {
        finalize(message.values);
      } else if (message?.type === "cancel") {
        finalize(undefined);
      }
    });

    const disposeDisposable = panel.onDidDispose(() => {
      finalize(undefined);
    });

    panel.onDidDispose(() => {
      messageDisposable.dispose();
      disposeDisposable.dispose();
    });
  });
}

module.exports = {
  showFormBox
};
