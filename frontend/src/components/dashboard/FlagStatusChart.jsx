import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#6dffb0", "#5c6680"];

function FlagStatusChart({ data }) {
  return (
    <article className="dashboard-chart-card">
      <div className="chart-card-heading"><div><p className="dashboard-eyebrow">Status distribution</p><h3>Flag Status</h3></div></div>
      {data.length === 0 ? <p className="chart-empty">No feature flags are available yet.</p> : (
        <div className="chart-body chart-body-pie">
          <ResponsiveContainer width="100%" height={230}>
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={58} outerRadius={86} paddingAngle={4}>
                {data.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#151c2c", border: "1px solid rgba(255,255,255,.12)", borderRadius: 8, color: "#f5f7ff" }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="chart-legend">{data.map((entry, index) => <span key={entry.name}><i style={{ background: COLORS[index % COLORS.length] }} />{entry.name}<strong>{entry.value}</strong></span>)}</div>
        </div>
      )}
    </article>
  );
}

export default FlagStatusChart;
