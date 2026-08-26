import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

function FlagTypesChart({ data }) {
  return (
    <article className="dashboard-chart-card">
      <div className="chart-card-heading"><div><p className="dashboard-eyebrow">Configuration mix</p><h3>Flag Types</h3></div></div>
      {data.length === 0 ? <p className="chart-empty">No flag types are available yet.</p> : (
        <ResponsiveContainer width="100%" height={270}>
          <BarChart data={data} layout="vertical" margin={{ top: 4, right: 18, left: 8, bottom: 4 }}>
            <CartesianGrid stroke="rgba(255,255,255,.07)" horizontal={false} />
            <XAxis type="number" allowDecimals={false} tick={{ fill: "#69738a", fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="type" width={68} tick={{ fill: "#8b95ab", fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip cursor={{ fill: "rgba(124,141,255,.08)" }} contentStyle={{ background: "#151c2c", border: "1px solid rgba(255,255,255,.12)", borderRadius: 8, color: "#f5f7ff" }} />
            <Bar dataKey="flags" fill="#45a7ff" radius={[0, 5, 5, 0]} name="Flags" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </article>
  );
}

export default FlagTypesChart;
