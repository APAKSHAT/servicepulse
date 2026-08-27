import { useCallback, useEffect, useState } from "react";
import {
  HiChartBar,
  HiExclamationTriangle,
  HiPlus,
  HiSignal,
} from "react-icons/hi2";
import {
  createEndpoint,
  deleteEndpoint,
  fetchEndpoints,
  fetchIncidents,
  fetchSummary,
} from "./api";
import AddEndpointForm from "./components/AddEndpointForm";
import Dashboard from "./components/Dashboard";
import EndpointList from "./components/EndpointList";
import IncidentPanel from "./components/IncidentPanel";
import "./index.css";

const VIEWS = { DASHBOARD: "dashboard", ENDPOINTS: "endpoints", INCIDENTS: "incidents" };

export default function App() {
  const [view, setView] = useState(VIEWS.DASHBOARD);
  const [showForm, setShowForm] = useState(false);
  const [endpoints, setEndpoints] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [summary, setSummary] = useState({
    total_endpoints: 0,
    active_endpoints: 0,
    active_incidents: 0,
    overall_uptime_pct: 0,
  });

  const loadData = useCallback(async () => {
    try {
      const [ep, inc, sum] = await Promise.all([
        fetchEndpoints(),
        fetchIncidents(),
        fetchSummary(),
      ]);
      setEndpoints(ep);
      setIncidents(inc);
      setSummary(sum);
    } catch (err) {
      console.error("Failed to load data", err);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, [loadData]);

  async function handleCreate(payload) {
    try {
      await createEndpoint(payload);
      setShowForm(false);
      await loadData();
    } catch (err) {
      console.error("Failed to create endpoint", err);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteEndpoint(id);
      await loadData();
    } catch (err) {
      console.error("Failed to delete endpoint", err);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="dot" />
          <span>ServicePulse</span>
        </div>
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${view === VIEWS.DASHBOARD ? "active" : ""}`}
            onClick={() => setView(VIEWS.DASHBOARD)}
          >
            <HiChartBar size={18} />
            <span>Dashboard</span>
          </button>
          <button
            className={`nav-item ${view === VIEWS.ENDPOINTS ? "active" : ""}`}
            onClick={() => setView(VIEWS.ENDPOINTS)}
          >
            <HiSignal size={18} />
            <span>Endpoints</span>
          </button>
          <button
            className={`nav-item ${view === VIEWS.INCIDENTS ? "active" : ""}`}
            onClick={() => setView(VIEWS.INCIDENTS)}
          >
            <HiExclamationTriangle size={18} />
            <span>Incidents</span>
          </button>
        </nav>
      </aside>

      <main className="main-content">
        {view === VIEWS.DASHBOARD && (
          <Dashboard
            summary={summary}
            incidents={incidents}
            endpoints={endpoints}
            onSelectEndpoint={(ep) => setView(VIEWS.ENDPOINTS)}
          />
        )}

        {view === VIEWS.ENDPOINTS && (
          <>
            <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h1>Endpoints</h1>
                <p>Manage the URLs you are monitoring</p>
              </div>
              <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                <HiPlus size={16} />
                Add Endpoint
              </button>
            </div>
            <div className="card">
              <EndpointList
                endpoints={endpoints}
                onSelect={() => {}}
                onDelete={handleDelete}
              />
            </div>
          </>
        )}

        {view === VIEWS.INCIDENTS && (
          <>
            <div className="page-header">
              <h1>Incidents</h1>
              <p>Grouped failure events across all endpoints</p>
            </div>
            <IncidentPanel incidents={incidents} />
          </>
        )}
      </main>

      {showForm && (
        <AddEndpointForm
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}
    </div>
  );
}
