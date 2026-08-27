import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function UptimeChart({ checks }) {
  if (!checks || checks.length === 0) {
    return (
      <div className="chart-container card">
        <h3>Uptime</h3>
        <div className="empty-state">
          <p>No check data yet.</p>
        </div>
      </div>
    );
  }

  // Group checks into 30-minute buckets and compute uptime % per bucket.
  const bucketMs = 30 * 60 * 1000;
  const buckets = new Map();

  for (const c of checks) {
    const t = new Date(c.checked_at).getTime();
    const key = Math.floor(t / bucketMs) * bucketMs;
    if (!buckets.has(key)) buckets.set(key, { total: 0, ok: 0 });
    const b = buckets.get(key);
    b.total += 1;
    if (c.status_code !== null && c.status_code < 400) b.ok += 1;
  }

  const data = [...buckets.entries()]
    .sort(([a], [b]) => a - b)
    .map(([ts, b]) => ({
      time: new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      uptime: Math.round((b.ok / b.total) * 100),
    }));

  return (
    <div className="chart-container card">
      <h3>Uptime %</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="uptimeGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3345" />
          <XAxis dataKey="time" tick={{ fill: "#6b7280", fontSize: 11 }} />
          <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              background: "#21242f",
              border: "1px solid #2e3345",
              borderRadius: 8,
              fontSize: 13,
            }}
            labelStyle={{ color: "#9aa0b0" }}
          />
          <Area
            type="monotone"
            dataKey="uptime"
            stroke="#22c55e"
            strokeWidth={2}
            fill="url(#uptimeGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
