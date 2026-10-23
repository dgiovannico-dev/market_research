#!/usr/bin/env node
/**
 * FSD import-boundary checker (pragmatic for this repo).
 *
 * Layers (high → low): app → widgets → features → entities → shared
 *
 * Rules:
 * - Never import a higher layer.
 * - widgets must not import other widgets (compose in app pages).
 * - features/entities may import sibling slices via public API only
 *   (no `/ui/` or `/model/` deep paths across slices).
 * - shared has segments (api|hooks|lib|ui), not product slices — free
 *   cross-segment imports inside shared; shared must not import up.
 */
import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();
const LAYERS = ["app", "widgets", "features", "entities", "shared"];
const LAYER_RANK = Object.fromEntries(LAYERS.map((l, i) => [l, i]));

const IMPORT_RE =
  /(?:from\s+|import\s*\(\s*)["'](@\/(app|widgets|features|entities|shared)\/[^"']+)["']/g;

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === "node_modules" || ent.name === ".next") continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, out);
    else if (/\.(ts|tsx)$/.test(ent.name) && !ent.name.endsWith(".test.ts")) {
      out.push(p);
    }
  }
  return out;
}

function layerOf(filePath) {
  const rel = path.relative(ROOT, filePath).replaceAll("\\", "/");
  const top = rel.split("/")[0];
  return LAYER_RANK[top] != null ? top : null;
}

function sliceOfImport(absImport, layer) {
  const rest = absImport.replace(`@/${layer}/`, "");
  return rest.split("/")[0] || null;
}

function fileSlice(filePath, layer) {
  const rel = path.relative(ROOT, filePath).replaceAll("\\", "/");
  const parts = rel.split("/");
  if (parts[0] !== layer) return null;
  return parts[1] || null;
}

function isDeepCrossSlice(absImport, layer, fromSlice) {
  const toSlice = sliceOfImport(absImport, layer);
  if (!toSlice || !fromSlice || toSlice === fromSlice) return false;
  // Public API: @/features/foo or @/features/foo/index — OK
  // Deep: @/features/foo/ui/... or /model/ — forbidden across slices
  const rest = absImport.replace(`@/${layer}/${toSlice}`, "");
  return rest.startsWith("/ui/") || rest.startsWith("/model/") || rest.startsWith("/api/");
}

const errors = [];
const files = [];
for (const layer of LAYERS) walk(path.join(ROOT, layer), files);

for (const file of files) {
  const fromLayer = layerOf(file);
  if (!fromLayer) continue;
  const fromRank = LAYER_RANK[fromLayer];
  const fromSlice = fileSlice(file, fromLayer);
  const text = fs.readFileSync(file, "utf8");
  const relFile = path.relative(ROOT, file).replaceAll("\\", "/");

  let m;
  IMPORT_RE.lastIndex = 0;
  while ((m = IMPORT_RE.exec(text))) {
    const abs = m[1];
    const toLayer = m[2];
    const toRank = LAYER_RANK[toLayer];

    if (toRank < fromRank) {
      errors.push(`${relFile}: cannot import higher layer ${abs}`);
      continue;
    }

    if (fromLayer === "shared") {
      // segments are free inside shared
      continue;
    }

    if (fromLayer === "app") continue;

    if (fromLayer === "widgets" && toLayer === "widgets") {
      const toSlice = sliceOfImport(abs, "widgets");
      if (toSlice && fromSlice && toSlice !== fromSlice) {
        errors.push(
          `${relFile}: widget→widget import ${abs} (compose in app page instead)`,
        );
      }
      continue;
    }

    if (
      (fromLayer === "features" || fromLayer === "entities") &&
      toLayer === fromLayer
    ) {
      if (isDeepCrossSlice(abs, toLayer, fromSlice)) {
        errors.push(
          `${relFile}: deep same-layer import ${abs} (use slice public API)`,
        );
      }
    }
  }
}

if (errors.length) {
  console.error(`FSD import violations (${errors.length}):\n`);
  for (const e of errors.slice(0, 80)) console.error(` - ${e}`);
  if (errors.length > 80) console.error(` … +${errors.length - 80} more`);
  process.exit(1);
}

console.log(`FSD import check OK (${files.length} files)`);
