import assert from "node:assert/strict";
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { validateCiSyncContract } from "./validate_ci_sync.mjs";

const repositoryRoot = fileURLToPath(new URL("../../../", import.meta.url));
const contract = JSON.parse(
  readFileSync(join(repositoryRoot, ".github/ci-sync.json"), "utf8"),
);

function writeManifest(root, manifest) {
  writeFileSync(join(root, ".github/ci-sync.json"), JSON.stringify(manifest));
}

function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), "hato-bot-ci-sync-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  for (const file of [...contract.files, ".github/ci-sync.json"]) {
    mkdirSync(dirname(join(root, file)), { recursive: true });
    writeFileSync(join(root, file), "fixture\n");
  }
  writeManifest(root, contract);
  return { root, manifest: structuredClone(contract) };
}

test("the checked-in contract includes all shared settings and validates", () => {
  assert.deepEqual(validateCiSyncContract(repositoryRoot), contract);
  assert.deepEqual(contract.excludeWorkflows, [
    "*hato-bot.yml",
    "verify-lockfile.yml",
  ]);
  assert.equal(contract.files.length, 15);
});

test("a complete source checkout validates", (t) => {
  const { root, manifest } = fixture(t);
  assert.deepEqual(validateCiSyncContract(root), manifest);
});

test("unsupported versions, missing keys and unknown keys fail closed", (t) => {
  const { root, manifest } = fixture(t);
  for (const invalid of [
    null,
    [],
    { ...manifest, schemaVersion: 2 },
    { ...manifest, schemaVersion: "1" },
    { files: manifest.files, excludeWorkflows: manifest.excludeWorkflows },
    { ...manifest, extra: true },
  ]) {
    writeManifest(root, invalid);
    assert.throws(() => validateCiSyncContract(root));
  }
});

test("invalid arrays and duplicate entries fail closed", (t) => {
  const { root, manifest } = fixture(t);
  for (const key of ["files", "excludeWorkflows"]) {
    for (const invalid of [
      null,
      "not-an-array",
      [],
      [""],
      [1],
      [...manifest[key], manifest[key][0]],
    ]) {
      writeManifest(root, { ...manifest, [key]: invalid });
      assert.throws(() => validateCiSyncContract(root));
    }
  }
});

test("absolute paths, traversal and ambiguous paths are rejected", (t) => {
  const { root, manifest } = fixture(t);
  for (const file of [
    "/etc/passwd",
    "../outside",
    "dir/../aqua.yaml",
    "./aqua.yaml",
    "dir//aqua.yaml",
    "dir/",
    "dir\\aqua.yaml",
    "C:/aqua.yaml",
    "aqua.yaml\n",
    "*.yaml",
  ]) {
    writeManifest(root, { ...manifest, files: [...manifest.files, file] });
    assert.throws(() => validateCiSyncContract(root), /Unsafe relative path/);
  }
});

test("workflow exclusions must be filename patterns, not paths", (t) => {
  const { root, manifest } = fixture(t);
  for (const pattern of [
    "../*.yml",
    "/codeql.yml",
    "dir/codeql.yml",
    "dir\\file.yml",
    "*",
    "file.yml\n",
  ]) {
    writeManifest(root, { ...manifest, excludeWorkflows: [pattern] });
    assert.throws(
      () => validateCiSyncContract(root),
      /Unsafe workflow filename pattern/,
    );
  }
});

test("both Aqua files must remain in the contract", (t) => {
  const { root, manifest } = fixture(t);
  for (const removed of [
    ["aqua.yaml"],
    ["aqua-checksums.json"],
    ["aqua.yaml", "aqua-checksums.json"],
  ]) {
    writeManifest(root, {
      ...manifest,
      files: manifest.files.filter((file) => !removed.includes(file)),
    });
    assert.throws(() => validateCiSyncContract(root), /must include both aqua/);
  }
});

test("missing shared files, including Aqua checksums, are rejected", (t) => {
  const { root } = fixture(t);
  rmSync(join(root, "aqua-checksums.json"));
  assert.throws(() => validateCiSyncContract(root), /ENOENT/);
});

test("missing and malformed manifests are rejected", (t) => {
  const { root } = fixture(t);
  writeFileSync(join(root, ".github/ci-sync.json"), "not JSON");
  assert.throws(() => validateCiSyncContract(root), SyntaxError);
  rmSync(join(root, ".github/ci-sync.json"));
  assert.throws(() => validateCiSyncContract(root), /ENOENT/);
});

test("directories cannot stand in for shared files", (t) => {
  const { root } = fixture(t);
  rmSync(join(root, "aqua.yaml"));
  mkdirSync(join(root, "aqua.yaml"));
  assert.throws(() => validateCiSyncContract(root), /not a regular file/);
});

test("shared files and their parent directories cannot be symlinks", (t) => {
  const { root } = fixture(t);
  rmSync(join(root, "aqua.yaml"));
  symlinkSync(join(root, "aqua-checksums.json"), join(root, "aqua.yaml"));
  assert.throws(() => validateCiSyncContract(root), /must not use symlinks/);

  rmSync(join(root, ".github"), { recursive: true });
  mkdirSync(join(root, "real-github"));
  symlinkSync(join(root, "real-github"), join(root, ".github"));
  writeManifest(root, contract);
  assert.throws(() => validateCiSyncContract(root), /must not use symlinks/);
});

test("the manifest and repository root cannot be symlinks", (t) => {
  const { root } = fixture(t);
  writeFileSync(join(root, "real-manifest.json"), JSON.stringify(contract));
  rmSync(join(root, ".github/ci-sync.json"));
  symlinkSync(
    join(root, "real-manifest.json"),
    join(root, ".github/ci-sync.json"),
  );
  assert.throws(() => validateCiSyncContract(root), /must not use symlinks/);

  const rootLink = join(root, "root-link");
  symlinkSync(root, rootLink, "dir");
  assert.throws(
    () => validateCiSyncContract(rootLink),
    /root must be a directory/,
  );
});
