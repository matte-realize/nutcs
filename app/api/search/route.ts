import { NextRequest, NextResponse } from "next/server";
import { getDb, type Course } from "@/lib/db";

export const dynamic = "force-dynamic";

// Whitelisted sort columns — never interpolate user input into SQL directly.
const SORT_COLUMNS: Record<string, string> = {
  institution: "institution_name",
  course: "course_code",
  transfer: "transfer_credit",
  nupath: "nupath",
  nucore: "nucore",
  state: "state",
};

const PAGE_SIZE = 50;
const MAX_PAGE_SIZE = 200;

export function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const q = (sp.get("q") || "").trim();
  const state = (sp.get("state") || "").trim();
  const city = (sp.get("city") || "").trim();
  const country = (sp.get("country") || "").trim();

  const sortKey = sp.get("sort") || "institution";
  const sortCol = SORT_COLUMNS[sortKey] || "institution_name";
  const dir = sp.get("dir") === "desc" ? "DESC" : "ASC";

  const page = Math.max(1, parseInt(sp.get("page") || "1", 10) || 1);
  const pageSize = Math.min(
    MAX_PAGE_SIZE,
    Math.max(1, parseInt(sp.get("pageSize") || String(PAGE_SIZE), 10) || PAGE_SIZE)
  );

  const where: string[] = [];
  const params: Record<string, string | number> = {};

  if (q) {
    // Search bar matches institution name OR the NU transfer-credit text.
    where.push("(institution_name LIKE @q OR transfer_credit LIKE @q)");
    params.q = `%${q}%`;
  }
  if (state) {
    where.push("state = @state");
    params.state = state;
  }
  if (city) {
    where.push("city = @city");
    params.city = city;
  }
  if (country) {
    where.push("country = @country");
    params.country = country;
  }

  const whereSql = where.length ? `WHERE ${where.join(" AND ")}` : "";
  const db = getDb();

  const total = (
    db
      .prepare(`SELECT COUNT(*) AS n FROM courses ${whereSql}`)
      .get(params) as { n: number }
  ).n;

  const results = db
    .prepare(
      `SELECT id, institution_name, city, state, country, department,
              course_code, transfer_credit, effective_date, nucore, nupath
       FROM courses
       ${whereSql}
       ORDER BY ${sortCol} ${dir}, institution_name ASC, course_code ASC
       LIMIT @limit OFFSET @offset`
    )
    .all({ ...params, limit: pageSize, offset: (page - 1) * pageSize }) as Course[];

  return NextResponse.json({ results, total, page, pageSize });
}
