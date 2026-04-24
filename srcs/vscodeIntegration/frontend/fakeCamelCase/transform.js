function toFakeCamelCase(identifier) {
  const parts = identifier.split("_");
  if (parts.length < 2) {
    return identifier;
  }

  return parts[0] + parts.slice(1).map((part) => {
    if (!part) {
      return "";
    }
    return part[0].toUpperCase() + part.slice(1);
  }).join("");
}

function isIdentifierChar(char) {
  return /[A-Za-z0-9_]/.test(char);
}

function isIdentifierStart(char) {
  return /[a-z]/.test(char);
}

function isEscaped(text, index) {
  let backslashCount = 0;
  for (let cursor = index - 1; cursor >= 0 && text[cursor] === "\\"; cursor -= 1) {
    backslashCount += 1;
  }
  return backslashCount % 2 === 1;
}

function isAtIncludeDirective(text, index) {
  const lineStart = text.lastIndexOf("\n", index - 1) + 1;
  const prefix = text.slice(lineStart, index);
  if (!/^\s*$/.test(prefix)) {
    return false;
  }

  return /^#\s*include\b/.test(text.slice(index));
}

function findLineEnd(text, index) {
  const lineEnd = text.indexOf("\n", index);
  return lineEnd === -1 ? text.length : lineEnd;
}

function findFakeCamelCaseMatches(text, startIndex = 0) {
  const matches = [];
  let cursor = 0;
  let inLineComment = false;
  let inBlockComment = false;
  let inString = false;
  let inChar = false;

  while (cursor < text.length) {
    const char = text[cursor];
    const nextChar = text[cursor + 1] ?? "";

    if (inLineComment) {
      if (char === "\n") {
        inLineComment = false;
      }
      cursor += 1;
      continue;
    }

    if (inBlockComment) {
      if (char === "*" && nextChar === "/") {
        inBlockComment = false;
        cursor += 2;
        continue;
      }
      cursor += 1;
      continue;
    }

    if (inString) {
      if (char === "\"" && !isEscaped(text, cursor)) {
        inString = false;
      }
      cursor += 1;
      continue;
    }

    if (inChar) {
      if (char === "'" && !isEscaped(text, cursor)) {
        inChar = false;
      }
      cursor += 1;
      continue;
    }

    if (char === "/" && nextChar === "/") {
      inLineComment = true;
      cursor += 2;
      continue;
    }

    if (char === "/" && nextChar === "*") {
      inBlockComment = true;
      cursor += 2;
      continue;
    }

    if (char === "#" && isAtIncludeDirective(text, cursor)) {
      cursor = findLineEnd(text, cursor);
      continue;
    }

    if (char === "\"") {
      inString = true;
      cursor += 1;
      continue;
    }

    if (char === "'") {
      inChar = true;
      cursor += 1;
      continue;
    }

    if (!isIdentifierStart(char)) {
      cursor += 1;
      continue;
    }

    const previousChar = cursor > 0 ? text[cursor - 1] : "";
    if (previousChar && isIdentifierChar(previousChar)) {
      cursor += 1;
      continue;
    }

    let end = cursor + 1;
    while (end < text.length && isIdentifierChar(text[end])) {
      end += 1;
    }

    const source = text.slice(cursor, end);
    const nextBoundaryChar = end < text.length ? text[end] : "";
    if (
      source.includes("_")
      && /^(?:[a-z][A-Za-z0-9]*)(?:_[A-Za-z0-9]+)+$/.test(source)
      && (!nextBoundaryChar || !isIdentifierChar(nextBoundaryChar))
      && cursor >= startIndex
    ) {
      const display = toFakeCamelCase(source);
      if (display !== source) {
        matches.push({
          index: cursor,
          source,
          display
        });
      }
    }

    cursor = end;
  }

  return matches;
}

module.exports = {
  toFakeCamelCase,
  findFakeCamelCaseMatches
};
