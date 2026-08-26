function Dashboard() {
  return (
    <section className="dashboard-placeholder">
      <div className="overview-intro">
        <p className="dashboard-eyebrow">Release control center</p>
        <h2>Build safer releases, one decision at a time.</h2>
        <p>Your workspace is ready for feature flags, environments, and controlled rollouts.</p>
      </div>
      <div className="overview-empty-state">
        <div className="empty-state-mark" aria-hidden="true">◈</div>
        <h3>Your workspace is taking shape</h3>
        <p>Connect your release workflow here as dashboard data becomes available.</p>
      </div>
    </section>
  );
}

export default Dashboard;
