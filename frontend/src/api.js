import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// ── Endpoints ──────────────────────────────────────────────

export function fetchEndpoints() {
  return api.get("/api/endpoints").then((r) => r.data);
}

export function createEndpoint(payload) {
  return api.post("/api/endpoints", payload).then((r) => r.data);
}

export function deleteEndpoint(id) {
  return api.delete(`/api/endpoints/${id}`);
}

// ── Checks ─────────────────────────────────────────────────

export function fetchChecks(endpointId, hours = 24) {
  return api
    .get(`/api/endpoints/${endpointId}/checks`, { params: { hours } })
    .then((r) => r.data);
}

// ── Incidents ──────────────────────────────────────────────

export function fetchIncidents(status = "all") {
  return api
    .get("/api/incidents", { params: { status } })
    .then((r) => r.data);
}

// ── Dashboard ──────────────────────────────────────────────

export function fetchSummary() {
  return api.get("/api/dashboard/summary").then((r) => r.data);
}

export default api;
