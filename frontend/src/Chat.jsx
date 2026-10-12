import { useState } from "react";
import { api } from "./api.js";

const EXAMPLES = ["Which drives are at risk?", "Which drives are hottest?"];

export default function Chat({ onChanged }) {
  const [log, setLog] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  async function send(message) {
    if (!message.trim() || busy) return;
    setLog((l) => [...l, { role: "user", text: message }]);
    setText("");
    setBusy(true);
    try {
      const r = await api.chat(message);
      setLog((l) => [...l, { role: "ai", text: r.answer, meta: r }]);
      if (r.tools_used.includes("create_incident")) onChanged();
    } catch (e) {
      setLog((l) => [...l, { role: "ai", text: "Error: " + e.message }]);
    }
    setBusy(false);
  }

  return (
    <section className="panel">
      <h2>Copilot</h2>
      <div className="chat">
        {!log.length && (
          <p className="muted">
            Ask about a drive, e.g. “Why is drive 17 at high risk?” or “Create an incident for drive 17”.
          </p>
        )}
        {log.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <p>{m.text}</p>
            {m.meta && (
              <small className="muted">
                tools: {m.meta.tools_used.join(", ") || "none"}
                {m.meta.sources.length ? ` · sources: ${m.meta.sources.join(", ")}` : ""}
              </small>
            )}
          </div>
        ))}
        {busy && <p className="muted">Thinking…</p>}
      </div>
      <div className="row wrap">
        {EXAMPLES.map((e) => (
          <button key={e} className="ghost" onClick={() => send(e)}>{e}</button>
        ))}
      </div>
      <form className="row" onSubmit={(e) => { e.preventDefault(); send(text); }}>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ask the copilot…" maxLength={1000} />
        <button disabled={busy}>Send</button>
      </form>
    </section>
  );
}
