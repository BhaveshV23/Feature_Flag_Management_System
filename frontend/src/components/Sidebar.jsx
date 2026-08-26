function Sidebar() {
  return (
    <aside className="dashboard-sidebar" aria-label="Dashboard navigation">
      <strong>FlagFlow</strong>
      <nav>
        <a href="/dashboard">Overview</a>
        <a href="/features">Feature Flags</a>
        <a href="/environments">Environments</a>
        <a href="/rollouts">Rollouts</a>
      </nav>
    </aside>
  );
}

export default Sidebar;
