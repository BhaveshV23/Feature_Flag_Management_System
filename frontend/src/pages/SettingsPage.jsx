import { Link } from "react-router-dom";
import useAuth from "../hooks/useAuth";

const workspaceLinks = [
  { label: "Feature Flags", description: "Manage application release controls.", to: "/features", icon: "▣" },
  { label: "Environments", description: "Review configured release contexts.", to: "/environments", icon: "◈" },
  { label: "Rollouts", description: "Monitor percentage rollout rules.", to: "/rollouts", icon: "◒" },
  { label: "Analytics", description: "Explore configuration intelligence.", to: "/analytics", icon: "◌" },
  { label: "Audit Logs", description: "Review recorded workspace changes.", to: "/audit-logs", icon: "≡" },
];

const unavailableItems = [
  { title: "Profile", message: "Profile management is not available yet." },
  { title: "Password & Security", message: "Password management is handled by the authentication service." },
  { title: "Notifications", message: "Notification preferences are not available yet." },
  { title: "Appearance", message: "Appearance preferences are not persisted yet." },
];

function SettingsPage() {
  const { isAuthenticated, logout } = useAuth();

  const signOut = () => {
    logout();
    window.location.replace("/");
  };

  return (
    <section className="settings-page">
      <div className="feature-page-header settings-page-header">
        <div>
          <p className="dashboard-eyebrow">Workspace administration</p>
          <h2>Settings</h2>
          <p>Manage your account access and workspace experience.</p>
        </div>
      </div>

      <div className="settings-primary-grid">
        <article className="settings-card settings-account-card">
          <div className="settings-card-heading">
            <div><p className="dashboard-eyebrow">Account</p><h3>Account &amp; Session</h3></div>
            <span className="settings-status-badge"><i aria-hidden="true" />Authenticated</span>
          </div>
          <div className="settings-session-details">
            <div><span>Signed-in status</span><strong>{isAuthenticated ? "Authenticated" : "Not authenticated"}</strong></div>
            <div><span>Authentication</span><strong>JWT Bearer Authentication</strong></div>
          </div>
          <p className="settings-card-copy">Account, profile, and security settings are currently managed by the authentication service.</p>
          <button className="btn secondary settings-signout" onClick={signOut} type="button">Sign out</button>
        </article>

        <article className="settings-card settings-workspace-card">
          <div className="settings-card-heading"><div><p className="dashboard-eyebrow">Workspace</p><h3>Workspace Access</h3></div><span className="settings-access-badge">Available</span></div>
          <p className="settings-card-copy">Use these shortcuts to manage the FlagFlow release workspace.</p>
          <nav className="settings-workspace-links" aria-label="Workspace shortcuts">
            {workspaceLinks.map((item) => <Link className="settings-workspace-link" key={item.to} to={item.to}><span className="settings-link-icon" aria-hidden="true">{item.icon}</span><span><strong>{item.label}</strong><small>{item.description}</small></span><span className="settings-link-arrow" aria-hidden="true">→</span></Link>)}
          </nav>
        </article>
      </div>

      <section className="settings-card settings-future-section">
        <div className="settings-section-heading"><div><p className="dashboard-eyebrow">Account controls</p><h3>Security &amp; Preferences</h3><p>These controls will become available when the authentication service supports persisted account settings.</p></div><span className="settings-future-badge">Future capability</span></div>
        <div className="settings-future-grid">
          {unavailableItems.map((item) => <article className="settings-future-item" key={item.title}><div className="settings-future-item-heading"><h4>{item.title}</h4><span>Unavailable</span></div><p>{item.message}</p></article>)}
        </div>
      </section>
    </section>
  );
}

export default SettingsPage;
