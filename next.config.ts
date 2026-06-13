import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const projectRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  // Pin the workspace root. A stray lockfile in the home directory otherwise
  // makes Next infer the wrong root, which breaks the data/nutcs.db file
  // tracing below on Vercel.
  turbopack: { root: projectRoot },

  // better-sqlite3 is a native module — keep it external so the bundler
  // doesn't try to bundle its .node binary.
  serverExternalPackages: ["better-sqlite3"],

  // Ensure the read-only SQLite file is traced into the serverless function
  // bundle on Vercel. Without this, the file is missing at runtime.
  outputFileTracingIncludes: {
    "/api/**": ["./data/nutcs.db"],
  },
};

export default nextConfig;
