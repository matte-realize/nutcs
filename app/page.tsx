"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./page.module.css";

type Course = {
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

type SearchResponse = {
  results: Course[];
  total: number;
  page: number;
  pageSize: number;
};

const COLUMNS: { key: string; label: string; sortable: boolean }[] = [
  { key: "institution", label: "Institution", sortable: true },
  { key: "course", label: "Course", sortable: true },
  { key: "transfer", label: "Transfers as (NU)", sortable: true },
  { key: "nupath", label: "NUpath", sortable: true },
  { key: "nucore", label: "NUcore", sortable: true },
  { key: "state", label: "Location", sortable: true },
];

export default function Home() {
  const [q, setQ] = useState("");
  const [state, setState] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [sort, setSort] = useState("institution");
  const [dir, setDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);

  const [states, setStates] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [countries, setCountries] = useState<string[]>([]);

  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Load filter dropdown options once.
  useEffect(() => {
    fetch("/api/filters")
      .then((r) => r.json())
      .then((d) => {
        setStates(d.states || []);
        setCountries(d.countries || []);
      })
      .catch(() => {});
  }, []);

  // Load the city options whenever the selected state or country changes, and
  // clear any previously chosen city that no longer applies.
  useEffect(() => {
    setCity("");
    if (!state && !country) {
      setCities([]);
      return;
    }
    const params = new URLSearchParams();
    if (state) params.set("state", state);
    if (country) params.set("country", country);
    fetch(`/api/filters?${params.toString()}`)
      .then((r) => r.json())
      .then((d) => setCities(d.cities || []))
      .catch(() => setCities([]));
  }, [state, country]);

  // Reset to page 1 when any query input changes.
  useEffect(() => {
    setPage(1);
  }, [q, state, city, country, sort, dir]);

  // Debounced search whenever inputs change.
  const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (debounce.current) clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      const params = new URLSearchParams({ sort, dir, page: String(page) });
      if (q) params.set("q", q);
      if (state) params.set("state", state);
      if (city) params.set("city", city);
      if (country) params.set("country", country);

      setLoading(true);
      fetch(`/api/search?${params.toString()}`)
        .then((r) => r.json())
        .then((d: SearchResponse) => setData(d))
        .catch(() => setData({ results: [], total: 0, page: 1, pageSize: 50 }))
        .finally(() => setLoading(false));
    }, 250);

    return () => {
      if (debounce.current) clearTimeout(debounce.current);
    };
  }, [q, state, city, country, sort, dir, page]);

  const totalPages = useMemo(
    () => (data ? Math.max(1, Math.ceil(data.total / data.pageSize)) : 1),
    [data]
  );

  function toggleSort(key: string) {
    if (sort === key) {
      setDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSort(key);
      setDir("asc");
    }
  }

  function clearAll() {
    setQ("");
    setState("");
    setCity("");
    setCountry("");
  }

  const hasFilters = q || state || city || country;

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>Northeastern University Transfer Credits Search</h1>
          <span className={styles.updated}>Last updated: September 2025</span>
        </div>
        <p className={styles.subtitle}>
          Find how courses from other institutions transfer as Northeastern University credit.
        </p>
      </header>

      <div className={styles.warning} role="note">
        <strong>Please note:</strong> You must be an <strong>unmatriculated</strong>{" "}
        student to be eligible to transfer these courses for credit. This tool is a
        guide only — always do a <strong>final check with your academic advisor</strong>{" "}
        to confirm credits will transfer.
      </div>

      <div className={styles.controls}>
        <div className={`${styles.field} ${styles.searchField}`}>
          <label className={styles.label} htmlFor="q">
            Search
          </label>
          <input
            id="q"
            className={styles.input}
            type="text"
            placeholder="Institution name or NU course (e.g. Adelphi, CHEM1211)…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label} htmlFor="state">
            State
          </label>
          <select
            id="state"
            className={styles.select}
            value={state}
            onChange={(e) => setState(e.target.value)}
          >
            <option value="">All states</option>
            {states.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label} htmlFor="city">
            City
          </label>
          <select
            id="city"
            className={styles.select}
            value={city}
            onChange={(e) => setCity(e.target.value)}
            disabled={!state && !country}
          >
            <option value="">
              {state || country ? "All cities" : "Select a state or country first"}
            </option>
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label} htmlFor="country">
            Country
          </label>
          <select
            id="country"
            className={styles.select}
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          >
            <option value="">All countries</option>
            {countries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {hasFilters && (
          <button className={styles.clearBtn} onClick={clearAll} type="button">
            Clear
          </button>
        )}
      </div>

      <p className={styles.meta}>
        {loading
          ? "Searching…"
          : data
          ? `${data.total.toLocaleString()} result${data.total === 1 ? "" : "s"}`
          : ""}
      </p>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className={col.sortable ? styles.sortable : undefined}
                  onClick={col.sortable ? () => toggleSort(col.key) : undefined}
                >
                  {col.label}
                  {sort === col.key ? (dir === "asc" ? " ▲" : " ▼") : ""}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data && data.results.length > 0 ? (
              data.results.map((r) => (
                <tr key={r.id}>
                  <td>{r.institution_name}</td>
                  <td>
                    <strong>{r.course_code}</strong>
                  </td>
                  <td className={styles.preserveLines}>{r.transfer_credit}</td>
                  <td className={styles.preserveLines}>{r.nupath || "—"}</td>
                  <td className={styles.preserveLines}>{r.nucore || "—"}</td>
                  <td>
                    {[r.city, r.state, r.country].filter(Boolean).join(", ") || "—"}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className={styles.empty} colSpan={COLUMNS.length}>
                  {loading ? "Searching…" : "No matching transfer credits found."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {data && data.total > data.pageSize && (
        <div className={styles.pagination}>
          <button
            className={styles.pageBtn}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1 || loading}
            type="button"
          >
            ← Prev
          </button>
          <span className={styles.meta}>
            Page {page} of {totalPages}
          </span>
          <button
            className={styles.pageBtn}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages || loading}
            type="button"
          >
            Next →
          </button>
        </div>
      )}
    </main>
  );
}
