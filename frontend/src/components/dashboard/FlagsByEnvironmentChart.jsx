import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function FlagsByEnvironmentChart({ data }) {
  return (
    <article className="dashboard-chart-card">
      <div className="chart-card-heading"><div><p className="dashboard-eyebrow">Environment coverage</p><h3>Flags by Environment</h3></div></div>
      {data.length === 0 ? <p className="chart-empty">No environment assignments are available yet.</p> : (
        <ResponsiveContainer width="100%" height={270}>
          <BarChart data={data} margin={{ top: 20, right: 8, left: -20, bottom: 4 }}>
            <CartesianGrid stroke="rgba(255,255,255,.07)" vertical={false} />
            <XAxis dataKey="environment" tick={{ fill: "#8b95ab", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis allowDecimals={false} tick={{ fill: "#69738a", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip cursor={{ fill: "rgba(124,141,255,.08)" }} contentStyle={{ background: "#151c2c", border: "1px solid rgba(255,255,255,.12)", borderRadius: 8, color: "#f5f7ff" }} />
            <Bar dataKey="flags" fill="#7c8dff" radius={[5, 5, 0, 0]} name="Flags" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </article>
  );
}

export default FlagsByEnvironmentChart;
