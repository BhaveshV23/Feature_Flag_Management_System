function EvaluationAnalyticsPlaceholder() {
  return (
    <article className="dashboard-chart-card evaluation-placeholder">
      <div className="chart-card-heading"><div><p className="dashboard-eyebrow">Telemetry</p><h3>Evaluation Analytics</h3></div><span className="coming-soon-badge">Awaiting data</span></div>
      <div className="evaluation-placeholder-content">
        <div className="empty-state-mark" aria-hidden="true">◌</div>
        <p>Evaluation analytics will appear here once evaluation telemetry is available.</p>
      </div>
    </article>
  );
}

export default EvaluationAnalyticsPlaceholder;
