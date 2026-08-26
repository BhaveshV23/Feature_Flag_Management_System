import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";

const pageTitles = {
  "/dashboard": "Overview",
  "/features": "Feature Flags",
  "/environments": "Environments",
  "/rollouts": "Rollouts",
  "/analytics": "Analytics",
  "/audit-logs": "Audit Logs",
  "/settings": "Settings",
};

function DashboardLayout({ onSignOut }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] || "Workspace";

  return (
    <div className="dashboard-layout">
      <div className={`dashboard-scrim${isSidebarOpen ? " is-visible" : ""}`} onClick={() => setIsSidebarOpen(false)} />
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} onSignOut={onSignOut} />
      <main className="dashboard-content">
        <header className="dashboard-topbar">
          <button className="dashboard-menu-button" aria-label="Open navigation menu" onClick={() => setIsSidebarOpen(true)} type="button">☰</button>
          <div className="dashboard-heading">
            <p className="dashboard-breadcrumb">Workspace / <span>{pageTitle}</span></p>
            <h1>{pageTitle}</h1>
          </div>
          <div className="dashboard-account">
            <div className="account-avatar" aria-hidden="true">A</div>
            <div className="account-copy"><strong>Admin</strong><span>Administrator</span></div>
            <button className="topbar-signout" onClick={onSignOut} type="button">Sign out</button>
          </div>
        </header>
        <div className="dashboard-page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;
