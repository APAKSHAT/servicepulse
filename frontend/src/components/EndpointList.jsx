import { HiTrash } from "react-icons/hi2";
import StatusBadge from "./StatusBadge";

export default function EndpointList({ endpoints, onSelect, onDelete }) {
  if (endpoints.length === 0) {
    return (
      <div className="empty-state">
        <div className="icon">📡</div>
        <p>No endpoints registered yet. Add one to start monitoring.</p>
      </div>
    );
  }

  return (
    <table className="endpoint-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>URL</th>
          <th>Status</th>
          <th>Latency</th>
          <th>Interval</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {endpoints.map((ep) => (
          <tr key={ep.id}>
            <td>
              <span
                className="name"
                style={{ cursor: "pointer" }}
                onClick={() => onSelect(ep)}
              >
                {ep.name}
              </span>
            </td>
            <td className="url">{ep.url}</td>
            <td>
              <StatusBadge statusCode={ep.latest_status} />
            </td>
            <td>
              {ep.latest_response_time_ms !== null
                ? `${Math.round(ep.latest_response_time_ms)} ms`
                : "—"}
            </td>
            <td>{ep.interval_seconds}s</td>
            <td>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => onDelete(ep.id)}
                title="Remove endpoint"
              >
                <HiTrash size={16} />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
