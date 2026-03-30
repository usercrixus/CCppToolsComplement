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

function findFakeCamelCaseMatches(text) {
  const matches = [];
  const pattern = /\b[a-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b/g;
  let match = pattern.exec(text);

  while (match) {
    const source = match[0];
    const display = toFakeCamelCase(source);
    if (display !== source) {
      matches.push({
        index: match.index,
        source,
        display
      });
    }
    match = pattern.exec(text);
  }

  return matches;
}

module.exports = {
  toFakeCamelCase,
  findFakeCamelCaseMatches
};
