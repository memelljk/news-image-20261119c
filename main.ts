/**
 * THE WHOLE DAY — Broadsheet Edition
 * make.fun entrypoint for competition news-image-20261119.
 *
 * Runs the deterministic PIL renderer (gazette.py) to produce a fresh
 * entry.png, validates it (PNG magic, 1024x1024, <= 1 MiB) and copies it
 * to MAKEFUN_OUTPUT_DIR ?? /output. If python3/PIL is unavailable, it
 * falls back to the committed entry.png.
 */
import { execFileSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const committed = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const outFile = join(outDir, "entry.png");

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1024 * 1024; // 1 MiB

function validatePng(path: string): void {
  const buf = readFileSync(path);
  if (buf.length > MAX_BYTES) {
    throw new Error(`${path} is ${buf.length} bytes, over the 1 MiB limit`);
  }
  if (!buf.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error(`${path} is not a PNG (bad magic bytes)`);
  }
  // IHDR: width/height are big-endian uint32 at offsets 16 and 20.
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    throw new Error(`${path} is ${width}x${height}, expected 1024x1024`);
  }
}

function renderFresh(): boolean {
  try {
    execFileSync("python3", [join(here, "gazette.py")], {
      stdio: "inherit",
      timeout: 120_000,
    });
    return existsSync(committed) && statSync(committed).size > 0;
  } catch (err) {
    console.warn(`Fresh render failed, using committed entry.png: ${err}`);
    return false;
  }
}

function main(): void {
  renderFresh();
  if (!existsSync(committed)) {
    throw new Error("entry.png missing and renderer unavailable");
  }
  validatePng(committed);
  mkdirSync(outDir, { recursive: true });
  copyFileSync(committed, outFile);
  validatePng(outFile);
  console.log(`entry.png -> ${outFile} (${statSync(outFile).size} bytes)`);
}

main();
