import { useCallback, useEffect, useState } from "react";
import { fetchChecks, fetchSummary } from "../api";
import IncidentPanel from "./IncidentPanel";
import LatencyChart from "./LatencyChart";
import UptimeChart from "./UptimeChart";

export default function Dashboard({ summary, incidents, endpoints, onSelectEndpoint }) {
  const [selectedId, setSelectedId] = useState(null);
  const [checks, setChecks] = useState([]);

  // Auto-select the first endpoint for charts.
  useEffect(() => {
    if (endpoints.length > 0 && selectedId === null) {
      setSelectedId(endpoints[0].id);
    }
  }, [endpoints, selectedId]);

  const loadChecks = useCallback(async () => {
    if (selectedId === null) return;
    try {
      const data = await fetchChecks(selectedId, 24);
      setChecks(data);
    } catch {
      setChecks([]);
    }
  }, [selectedId]);

  useEffect(() => {
    loadChecks();
    const interval = setInterval(loadChecks, 15000);
    return () => clearInterval(interval);
  }, [loadChecks]);

  const openIncidents = incidents.filter((i) => i.resolved_at === null);

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Real-time overview of your monitored services</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Total Endpoints</div>
          <div className="value accent">{summary.total_endpoints}</div>
        </div>
        <div className="stat-card">
          <div className="label">Active</div>
          <div className="value accent">{summary.active_endpoints}</div>
        </div>
        <div className="stat-card">
          <div className="label">Uptime (24h)</div>
          <div className="value success">{summary.overall_uptime_pct}%</div>
        </div>
        <div className="stat-card">
          <div className="label">Open Incidents</div>
          <div className={`value ${summary.active_incidents > 0 ? "danger" : "success"}`}>
            {summary.active_incidents}
          </div>
        </div>
      </div>

      {endpoints.length > 1 && (
        <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
          {endpoints.map((ep) => (
            <button
              key={ep.id}
              className={`btn btn-sm ${ep.id === selectedId ? "btn-primary" : "btn-ghost"}`}
              onClick={() => setSelectedId(ep.id)}
            >
              {ep.name}
            </button>
          ))}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <UptimeChart checks={checks} />
        <LatencyChart checks={checks} />
      </div>

      <IncidentPanel incidents={openIncidents} />
    </>
  );
}
