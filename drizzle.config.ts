import { defineConfig } from "drizzle-kit";
import * as schema from "./shared/schema";

export default defineConfig({
  out: "./migrations",
  schema: "./shared/schema.ts",
  dialect: "sqlite",
  dbCredentials: {
    url: "./data/pollyedge.db",
  },
});
