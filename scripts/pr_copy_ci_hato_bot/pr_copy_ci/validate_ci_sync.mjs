import { lstatSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const manifestPath = ".github/ci-sync.json";

function validateRelativePath(value) {
  if (
    typeof value !== "string" ||
    value.trim() !== value ||
    !/^[A-Za-z0-9_.-]+(?:\/[A-Za-z0-9_.-]+)*$/.test(value) ||
    value.split("/").some((part) => part === "." || part === "..")
  ) {
    throw new Error(`Unsafe relative path in CI sync contract: ${value}`);
  }
}

function validateRegularFile(repositoryRoot, relativePath) {
  validateRelativePath(relativePath);
  let currentPath = repositoryRoot;
  const parts = relativePath.split("/");

  for (const [index, part] of parts.entries()) {
    currentPath = join(currentPath, part);
    const metadata = lstatSync(currentPath);
    if (metadata.isSymbolicLink()) {
      throw new Error(`CI sync files must not use symlinks: ${relativePath}`);
    }
    if (
      index === parts.length - 1 ? !metadata.isFile() : !metadata.isDirectory()
    ) {
      throw new Error(`CI sync path is not a regular file: ${relativePath}`);
    }
  }
}

function validateUniqueStrings(values, name) {
  if (
    !Array.isArray(values) ||
    values.length === 0 ||
    values.some((value) => typeof value !== "string" || value.length === 0)
  ) {
    throw new Error(`${name} must be a non-empty array of strings`);
  }
  if (new Set(values).size !== values.length) {
    throw new Error(`${name} must not contain duplicates`);
  }
}

export function validateCiSyncContract(repositoryRoot = process.cwd()) {
  const root = resolve(repositoryRoot);
  const rootMetadata = lstatSync(root);
  if (rootMetadata.isSymbolicLink() || !rootMetadata.isDirectory()) {
    throw new Error(
      "CI sync repository root must be a directory, not a symlink",
    );
  }
  validateRegularFile(root, manifestPath);
  const manifest = JSON.parse(readFileSync(join(root, manifestPath), "utf8"));
  if (
    manifest === null ||
    typeof manifest !== "object" ||
    Array.isArray(manifest) ||
    Object.keys(manifest).sort().join(",") !==
      "excludeWorkflows,files,schemaVersion"
  ) {
    throw new Error(
      "CI sync contract must contain schemaVersion, files and excludeWorkflows only",
    );
  }
  if (manifest.schemaVersion !== 1) {
    throw new Error(
      `Unsupported CI sync schemaVersion: ${manifest.schemaVersion}`,
    );
  }

  validateUniqueStrings(manifest.files, "files");
  validateUniqueStrings(manifest.excludeWorkflows, "excludeWorkflows");
  if (
    !manifest.files.includes("aqua.yaml") ||
    !manifest.files.includes("aqua-checksums.json")
  ) {
    throw new Error(
      "CI sync contract must include both aqua.yaml and aqua-checksums.json",
    );
  }
  for (const file of manifest.files) {
    validateRegularFile(root, file);
  }
  for (const pattern of manifest.excludeWorkflows) {
    if (
      pattern.trim() !== pattern ||
      !/^[A-Za-z0-9_.*-]+\.ya?ml$/.test(pattern)
    ) {
      throw new Error(`Unsafe workflow filename pattern: ${pattern}`);
    }
  }
  return manifest;
}

if (
  process.argv[1] &&
  pathToFileURL(resolve(process.argv[1])).href === import.meta.url
) {
  try {
    const manifest = validateCiSyncContract(process.argv[2]);
    console.log(`Validated CI sync contract (${manifest.files.length} files)`);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
