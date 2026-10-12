import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import Chat from "./Chat.jsx";
import DriveDetail from "./DriveDetail.jsx";
import Incidents from "./Incidents.jsx";

const PAGE = 15;

export default function App() {
  const [stats, setStats] = useState(null);
  const [drives, setDrives] = useState({ total: 0, items: [] });
  const [incidents, setIncidents] = useState([]);
  const [level, setLevel] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const params = { limit: PAGE, offset: page * PAGE };
      if (level) params.risk_level = level;
      if (search) params.search = search;
      const [s, d, i] = await Promise.all([api.stats(), api.drives(params), api.incidents()]);
      setStats(s); setDrives(d); setIncidents(i); setError("");
    } catch (e) { setError("Cannot reach the API: " + e.message); }
  }, [level, search, page]);

  useEffect(() => { load(); }, [load]);

  const pages = Math.max(1, Math.ceil(drives.total / PAGE));
  const tile = (label, value, cls = "") => (
    <div className={`tile ${cls}`}><span>{label}</span><strong>{value ?? "–"}</strong></div>
  );

  return (
    <main>
      <header>
        <h1>AI Ops Copilot</h1>
        <p className="muted">Storage drive health monitoring (simulated data)</p>
      </header>
      {error && <p className="error" role="alert">{error}</p>}

      <div className="tiles">
        {tile("Total drives", stats?.total_drives)}
        {tile("Healthy", stats?.low, "LOW")}
        {tile("Medium risk", stats?.medium, "MEDIUM")}
        {tile("High risk", stats?.high, "HIGH")}
        {tile("Open incidents", stats?.open_incidents)}
      </div>

      <div className="grid">
        <section className="panel">
          <div className="row between wrap">
            <h2>Drives</h2>
            <div className="row">
              <input placeholder="Search name…" value={search}
                     onChange={(e) => { setSearch(e.target.value); setPage(0); }} />
              <select value={level} onChange={(e) => { setLevel(e.target.value); setPage(0); }}>
                <option value="">All risk levels</option>
                <option>HIGH</option><option>MEDIUM</option><option>LOW</option>
              </select>
            </div>
          </div>
          <table>
            <thead><tr><th>Drive</th><th>Temp</th><th>Sectors</th><th>Risk</th></tr></thead>
            <tbody>
              {drives.items.map((d) => (
                <tr key={d.id} onClick={() => setSelected(d.id)} className={selected === d.id ? "sel" : ""}
                    tabIndex={0} onKeyDown={(e) => e.key === "Enter" && setSelected(d.id)}>
                  <td>{d.name}</td>
                  <td>{d.latest?.temperature}°C</td>
                  <td>{d.latest?.reallocated_sectors}</td>
                  <td><span className={`badge ${d.risk_level}`}>{d.risk_level}</span> {d.risk_score.toFixed(2)}</td>
                </tr>
              ))}
              {!drives.items.length && <tr><td colSpan="4" className="muted">No drives match.</td></tr>}
            </tbody>
          </table>
          <div className="row between">
            <button className="ghost" disabled={page === 0} onClick={() => setPage(page - 1)}>← Prev</button>
            <span className="muted">Page {page + 1} of {pages} · {drives.total} drives</span>
            <button className="ghost" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>Next →</button>
          </div>
        </section>

        <div className="stack">
          {selected && <DriveDetail id={selected} onClose={() => setSelected(null)} onChanged={load} />}
          <Chat onChanged={load} />
          <Incidents items={incidents} onChanged={load} />
        </div>
      </div>
    </main>
  );
}
