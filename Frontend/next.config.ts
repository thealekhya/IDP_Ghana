import type { NextConfig } from "next";
import fs from "fs";
import path from "path";

const rootEnvPath = path.resolve(__dirname, "..", ".env");
if (fs.existsSync(rootEnvPath)) {
  for (const line of fs.readFileSync(rootEnvPath, "utf8").split(/\r?\n/)) {
    const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)\s*$/);
    if (!match || match[1].startsWith("#")) continue;
    const [, key, value] = match;
    process.env[key] = value.replace(/^["']|["']$/g, "");
  }
}

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;
