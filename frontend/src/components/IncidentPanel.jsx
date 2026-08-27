export default function IncidentPanel({ incidents }) {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="card">
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "#9aa0b0", marginBottom: 16 }}>
          Incidents
        </h3>
        <div className="empty-state">
          <div className="icon">✓</div>
          <p>No incidents. All systems operational.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 style={{ fontSize: 14, fontWeight: 600, color: "#9aa0b0", marginBottom: 16 }}>
        Incidents
      </h3>
      <div className="incident-list">
        {incidents.map((inc) => {
          const isResolved = inc.resolved_at !== null;
          const started = new Date(inc.started_at);
          const ended = isResolved ? new Date(inc.resolved_at) : new Date();
          const durationMin = Math.round((ended - started) / 60000);

          return (
            <div
              key={inc.id}
              className={`incident-item ${isResolved ? "resolved" : ""}`}
            >
              <div className="incident-info">
                <span className="name">
                  {inc.endpoint_name || `Endpoint #${inc.endpoint_id}`}
                </span>
                <span className="detail">
                  {isResolved ? "Resolved" : "Ongoing"} · {durationMin} min
                </span>
              </div>
              <div className="incident-meta">
                <div className="count">{inc.failure_count} failures</div>
                <div>{started.toLocaleString()}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
