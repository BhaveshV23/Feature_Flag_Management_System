function StatCard({ label, value, detail, tone }) {
  return (
    <article className="dashboard-stat-card">
      <div className={`stat-card-indicator ${tone || ""}`} aria-hidden="true" />
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{detail}</span>
    </article>
  );
}

export default StatCard;
