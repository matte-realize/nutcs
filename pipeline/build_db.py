"""
build_db.py — Offline data builder for the deployed app.

Reads the scraped JSON + the institution location CSV, applies the same
join + filter logic as database/cleanup.sql, and writes a single read-only
SQLite file (data/nutcs.db) with one denormalized `courses` table.

This .db file is what the Next.js app bundles and queries on Vercel — there
is no database server in production. Re-run this whenever the scraped data
changes, then commit data/nutcs.db and redeploy.

Stdlib only (json, csv, sqlite3) — no pip install required.

    python pipeline/build_db.py
"""

import os
import csv
import json
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
COURSES_JSON = os.path.join(DATA_DIR, "institutions_and_courses.json")
INSTITUTIONS_CSV = os.path.join(DATA_DIR, "genuni.csv")
DB_PATH = os.path.join(DATA_DIR, "nutcs.db")

# Rows excluded from the product view (mirrors database/cleanup.sql).
EXCLUDED_TRANSFER_CREDITS = {"NO TRANSFER -", "NO AP CREDIT -"}
EXCLUDED_INSTITUTIONS = {"Advanced Placement (admitted FL2025 & SP2026)"}


def load_locations(csv_path):
    """institution_name -> (city, state, country) from genuni.csv."""
    locations = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("institution_name") or "").strip()
            if name:
                locations[name] = (
                    (row.get("city") or "").strip(),
                    (row.get("state") or "").strip(),
                    (row.get("country") or "").strip(),
                )
    return locations


def iter_course_rows(courses_json, locations):
    """Yield cleaned, joined rows ready for insertion.

    Mirrors cleanup.sql:
      - INNER JOIN on institution_name (institution must exist in genuni.csv)
      - drop NO TRANSFER / NO AP CREDIT rows
      - drop the Advanced Placement bucket
    """
    with open(courses_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    for institution_name, institution_data in data.items():
        if institution_name in EXCLUDED_INSTITUTIONS:
            continue
        location = locations.get(institution_name)
        if location is None:  # INNER JOIN: skip institutions with no location row
            continue
        city, state, country = location

        for dept_name, courses in institution_data.get("departments", {}).items():
            for course_code, course_info in courses.items():
                # course_info = [transfer_credit, effective_date, nucore, nupath]
                info = list(course_info) + ["", "", "", ""]
                transfer_credit = info[0].strip()
                if transfer_credit in EXCLUDED_TRANSFER_CREDITS:
                    continue
                yield (
                    institution_name,
                    city,
                    state,
                    country,
                    dept_name,
                    course_code,
                    transfer_credit,
                    info[1].strip(),  # effective_date
                    info[2].strip(),  # nucore
                    info[3].strip(),  # nupath
                )


def build():
    locations = load_locations(INSTITUTIONS_CSV)
    rows = list(iter_course_rows(COURSES_JSON, locations))

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE courses (
                id               INTEGER PRIMARY KEY,
                institution_name TEXT NOT NULL,
                city             TEXT,
                state            TEXT,
                country          TEXT,
                department       TEXT,
                course_code      TEXT,
                transfer_credit  TEXT,
                effective_date   TEXT,
                nucore           TEXT,
                nupath           TEXT
            )
            """
        )
        cur.executemany(
            """
            INSERT INTO courses (
                institution_name, city, state, country, department,
                course_code, transfer_credit, effective_date, nucore, nupath
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        # Indexes for the filters the search UI will use.
        cur.execute("CREATE INDEX idx_courses_institution ON courses(institution_name)")
        cur.execute("CREATE INDEX idx_courses_state ON courses(state)")
        cur.execute("CREATE INDEX idx_courses_department ON courses(department)")
        cur.execute("CREATE INDEX idx_courses_course_code ON courses(course_code)")
        cur.execute("CREATE INDEX idx_courses_nupath ON courses(nupath)")
        cur.execute("CREATE INDEX idx_courses_nucore ON courses(nucore)")

        conn.commit()

        n_courses = cur.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        n_inst = cur.execute(
            "SELECT COUNT(DISTINCT institution_name) FROM courses"
        ).fetchone()[0]
    finally:
        conn.close()

    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"Built {DB_PATH}")
    print(f"  {n_courses:,} courses across {n_inst:,} institutions")
    print(f"  {size_mb:.2f} MB")


if __name__ == "__main__":
    build()
