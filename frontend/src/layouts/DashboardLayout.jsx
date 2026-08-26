import Sidebar from "../components/Sidebar";

function DashboardLayout({ children, onSignOut }) {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="dashboard-content">
        <button className="btn secondary" onClick={onSignOut} type="button">Sign out</button>
        {children}
      </main>
    </div>
  );
}

export default DashboardLayout;
