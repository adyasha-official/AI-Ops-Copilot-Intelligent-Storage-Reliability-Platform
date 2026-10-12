import { api } from "./api.js";

const NEXT = { OPEN: "IN_PROGRESS", IN_PROGRESS: "RESOLVED" };

export default function Incidents({ items, onChanged }) {
  async function advance(i) {
    await api.updateIncident(i.id, NEXT[i.status]);
    onChanged();
  }
  return (
    <section className="panel">
      <h2>Incidents</h2>
      {!items.length && <p className="muted">No incidents yet. Open a drive and click “Create incident”.</p>}
      <ul className="list">
        {items.map((i) => (
          <li key={i.id} className="row between">
            <span>
              #{i.id} · drive {i.drive_id} · <span className={`badge ${i.severity}`}>{i.severity}</span>{" "}
              <span className="muted">{i.status.replace("_", " ")}</span>
            </span>
            {NEXT[i.status] && (
              <button className="ghost" onClick={() => advance(i)}>
                → {NEXT[i.status].replace("_", " ")}
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
