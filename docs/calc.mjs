/**
 * Pure comparison logic for the envcheck web demo — a JS port of the same
 * rules used by envcheck/core.py, operating on raw text instead of file
 * paths (browsers can't read arbitrary paths, only file contents you
 * hand them). Kept dependency-free and DOM-free so it's unit-testable.
 */

/** Parse .env-style text into an ordered dict of key -> value. */
export function parseEnvText(text) {
  const values = {};
  if (!text) return values;

  for (const rawLine of text.split("\n")) {
    let line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    if (line.startsWith("export ")) line = line.slice("export ".length);
    const eq = line.indexOf("=");
    if (eq === -1) continue;
    let key = line.slice(0, eq).trim();
    let value = line.slice(eq + 1).trim();
    if (value.length >= 2 && value[0] === value[value.length - 1] && (value[0] === '"' || value[0] === "'")) {
      value = value.slice(1, -1);
    }
    if (key) values[key] = value;
  }
  return values;
}

/** Compare env text against example text; mirrors envcheck.core.compare(). */
export function compare(envText, exampleText) {
  const envValues = parseEnvText(envText);
  const exampleValues = parseEnvText(exampleText);

  const missing = Object.keys(exampleValues).filter((k) => !(k in envValues)).sort();
  const extra = Object.keys(envValues).filter((k) => !(k in exampleValues)).sort();
  const empty = Object.keys(envValues)
    .filter((k) => k in exampleValues && envValues[k] === "")
    .sort();

  return {
    missing,
    extra,
    empty,
    isClean: missing.length === 0 && empty.length === 0,
  };
}

/**
 * Fill in any keys from exampleText missing in envText, copying the
 * example's default value, without disturbing existing values. Mirrors
 * envcheck.core.scaffold(), returning the merged text plus how many keys
 * were added.
 */
export function scaffold(envText, exampleText) {
  const exampleValues = parseEnvText(exampleText);
  const existingValues = parseEnvText(envText);

  const toAdd = Object.keys(exampleValues).filter((k) => !(k in existingValues));
  if (toAdd.length === 0) {
    return { text: envText, added: 0 };
  }

  const lines = [];
  const trimmed = (envText || "").replace(/\n+$/, "");
  if (trimmed) lines.push(trimmed);
  for (const key of toAdd) {
    lines.push(`${key}=${exampleValues[key]}`);
  }
  return { text: lines.join("\n") + "\n", added: toAdd.length };
}
