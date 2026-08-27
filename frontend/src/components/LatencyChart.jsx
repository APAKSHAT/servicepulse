import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function LatencyChart({ checks }) {
  if (!checks || checks.length === 0) {
    return (
      <div className="chart-container card">
        <h3>Response Time</h3>
        <div className="empty-state">
          <p>No check data yet.</p>
        </div>
      </div>
    );
  }

  const data = checks
    .filter((c) => c.response_time_ms !== null)
    .map((c) => ({
      time: new Date(c.checked_at).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      latency: Math.round(c.response_time_ms),
    }));

  return (
    <div className="chart-container card">
      <h3>Response Time (ms)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3345" />
          <XAxis dataKey="time" tick={{ fill: "#6b7280", fontSize: 11 }} />
          <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              background: "#21242f",
              border: "1px solid #2e3345",
              borderRadius: 8,
              fontSize: 13,
            }}
            labelStyle={{ color: "#9aa0b0" }}
          />
          <Line
            type="monotone"
            dataKey="latency"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "#818cf8" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
