import { useEffect, useState } from "react";
import { api } from "./api.js";
import LineChart from "./LineChart.jsx";

export default function DriveDetail({ id, onClose, onChanged }) {
  const [drive, setDrive] = useState(null);
  const [hist, setHist] = useState([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    setDrive(null);
    Promise.all([api.drive(id), api.history(id)]).then(([d, h]) => { setDrive(d); setHist(h); });
  }, [id]);

  async function openIncident() {
    try {
      const inc = await api.createIncident({
        drive_id: id,
        description: `Opened from dashboard. Risk ${drive.risk_score} (${drive.risk_level}).`,
      });
      setMsg(`Incident #${inc.id} created`);
      onChanged();
    } catch (e) { setMsg("Failed: " + e.message); }
  }

  if (!drive) return <aside className="panel detail"><p>Loading…</p></aside>;
  const t = drive.latest;
  return (
    <aside className="panel detail">
      <div className="row between">
        <h2>{drive.name}</h2>
        <button className="ghost" onClick={onClose} aria-label="Close details">✕</button>
      </div>
      <p className="muted">{drive.model} · {drive.serial_number}</p>
      <p>
        <span className={`badge ${drive.risk_level}`}>{drive.risk_level}</span>{" "}
        risk score <strong>{drive.risk_score.toFixed(2)}</strong>
      </p>
      <dl className="kv">
        <dt>Temperature</dt><dd>{t.temperature} °C</dd>
        <dt>Reallocated sectors</dt><dd>{t.reallocated_sectors}</dd>
        <dt>Power-on hours</dt><dd>{t.power_on_hours.toLocaleString()}</dd>
        <dt>Seek error rate</dt><dd>{t.seek_error_rate}</dd>
      </dl>
      <div className="charts">
        <LineChart title="Temperature" unit="°C" points={hist.map((h) => h.temperature)} />
        <LineChart title="Reallocated sectors" points={hist.map((h) => h.reallocated_sectors)} color="var(--high)" />
        <LineChart title="Seek error rate" points={hist.map((h) => h.seek_error_rate)} color="var(--medium)" />
      </div>
      <button onClick={openIncident}>Create incident</button>
      {msg && <span className="muted"> {msg}</span>}
    </aside>
  );
}
