async function req(path, options) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  stats: () => req("/api/v1/stats"),
  drives: (params = {}) => req("/api/v1/drives?" + new URLSearchParams(params)),
  drive: (id) => req(`/api/v1/drives/${id}`),
  history: (id) => req(`/api/v1/drives/${id}/history`),
  incidents: () => req("/api/v1/incidents"),
  createIncident: (body) => req("/api/v1/incidents", { method: "POST", body: JSON.stringify(body) }),
  updateIncident: (id, status) =>
    req(`/api/v1/incidents/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
  chat: (message) => req("/api/v1/chat", { method: "POST", body: JSON.stringify({ message }) }),
};
