import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { parseEnvText, compare, scaffold } from "../calc.mjs";

describe("parseEnvText", () => {
  test("basic parsing", () => {
    assert.deepEqual(parseEnvText("FOO=bar\nBAZ=qux\n"), { FOO: "bar", BAZ: "qux" });
  });

  test("ignores comments and blank lines", () => {
    assert.deepEqual(parseEnvText("# hi\n\nFOO=bar\n  # indented\n"), { FOO: "bar" });
  });

  test("strips export prefix", () => {
    assert.deepEqual(parseEnvText("export FOO=bar\n"), { FOO: "bar" });
  });

  test("strips matching quotes", () => {
    assert.deepEqual(parseEnvText('FOO="bar"\nBAZ=\'qux\'\n'), { FOO: "bar", BAZ: "qux" });
  });

  test("empty/missing text returns empty object", () => {
    assert.deepEqual(parseEnvText(""), {});
    assert.deepEqual(parseEnvText(undefined), {});
  });

  test("skips malformed lines", () => {
    assert.deepEqual(parseEnvText("not-valid\nFOO=bar\n"), { FOO: "bar" });
  });
});

describe("compare", () => {
  test("detects missing keys", () => {
    const result = compare("FOO=bar\n", "FOO=\nBAZ=\n");
    assert.deepEqual(result.missing, ["BAZ"]);
    assert.deepEqual(result.extra, []);
    assert.deepEqual(result.empty, []);
  });

  test("detects extra keys", () => {
    const result = compare("FOO=bar\nSTALE=1\n", "FOO=\n");
    assert.deepEqual(result.extra, ["STALE"]);
  });

  test("detects empty values", () => {
    const result = compare("FOO=\n", "FOO=placeholder\n");
    assert.deepEqual(result.empty, ["FOO"]);
    assert.equal(result.isClean, false);
  });

  test("matching files are clean", () => {
    const result = compare("FOO=bar\nBAZ=qux\n", "FOO=\nBAZ=\n");
    assert.equal(result.isClean, true);
  });
});

describe("scaffold", () => {
  test("creates env from example when missing", () => {
    const result = scaffold("", "FOO=default\n");
    assert.equal(result.added, 1);
    assert.deepEqual(parseEnvText(result.text), { FOO: "default" });
  });

  test("preserves existing values", () => {
    const result = scaffold("FOO=custom\n", "FOO=default\nBAZ=other\n");
    assert.equal(result.added, 1);
    assert.deepEqual(parseEnvText(result.text), { FOO: "custom", BAZ: "other" });
  });

  test("no-op when already complete", () => {
    const result = scaffold("FOO=custom\n", "FOO=default\n");
    assert.equal(result.added, 0);
    assert.equal(result.text, "FOO=custom\n");
  });
});
