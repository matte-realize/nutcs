import path from "node:path";
import Database from "better-sqlite3";

// The read-only SQLite file is committed at data/nutcs.db and traced into the
// serverless bundle via next.config.ts (outputFileTracingIncludes).
const DB_PATH = path.join(process.cwd(), "data", "nutcs.db");

// Reuse a single connection across hot reloads / warm invocations.
const globalForDb = globalThis as unknown as { db?: Database.Database };

export function getDb(): Database.Database {
  if (!globalForDb.db) {
    globalForDb.db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
    globalForDb.db.pragma("journal_mode = OFF");
  }
  return globalForDb.db;
}

export type Course = {
  id: number;
  institution_name: string;
  city: string;
  state: string;
  country: string;
  department: string;
  course_code: string;
  transfer_credit: string;
  effective_date: string;
  nucore: string;
  nupath: string;
};
