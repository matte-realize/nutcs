import { NextRequest, NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export const dynamic = "force-dynamic";

// Distinct values for the State / Country / City dropdowns. Blank values are
// dropped. There are ~900 distinct cities, so cities are only returned when a
// state and/or country is supplied (?state=NY, ?country=Canada) — the UI
// scopes the city list to whichever location filters are active.
export function GET(req: NextRequest) {
  const db = getDb();
  const sp = req.nextUrl.searchParams;
  const state = (sp.get("state") || "").trim();
  const country = (sp.get("country") || "").trim();

  const states = (
    db
      .prepare(
        `SELECT DISTINCT state FROM courses
         WHERE state IS NOT NULL AND state != ''
         ORDER BY state ASC`
      )
      .all() as { state: string }[]
  ).map((r) => r.state);

  const countries = (
    db
      .prepare(
        `SELECT DISTINCT country FROM courses
         WHERE country IS NOT NULL AND country != ''
         ORDER BY country ASC`
      )
      .all() as { country: string }[]
  ).map((r) => r.country);

  let cities: string[] = [];
  if (state || country) {
    const cityWhere = ["city IS NOT NULL", "city != ''"];
    const cityParams: Record<string, string> = {};
    if (state) {
      cityWhere.push("state = @state");
      cityParams.state = state;
    }
    if (country) {
      cityWhere.push("country = @country");
      cityParams.country = country;
    }
    cities = (
      db
        .prepare(
          `SELECT DISTINCT city FROM courses
           WHERE ${cityWhere.join(" AND ")}
           ORDER BY city ASC`
        )
        .all(cityParams) as { city: string }[]
    ).map((r) => r.city);
  }

  return NextResponse.json({ states, countries, cities });
}
