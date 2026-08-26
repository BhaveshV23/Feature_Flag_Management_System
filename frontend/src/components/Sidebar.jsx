import { NavLink } from "react-router-dom";

const primaryLinks = [
  { label: "Overview", to: "/dashboard", icon: "⌂" },
  { label: "Feature Flags", to: "/features", icon: "▣" },
  { label: "Environments", to: "/environments", icon: "◈" },
  { label: "Rollouts", to: "/rollouts", icon: "◒" },
  { label: "Analytics", to: "/analytics", icon: "◌" },
  { label: "Audit Logs", to: "/audit-logs", icon: "≡" },
];

function Sidebar({ onSignOut, isOpen, onClose }) {
  return (
    <aside className={`dashboard-sidebar${isOpen ? " is-open" : ""}`} aria-label="Dashboard navigation">
      <div className="sidebar-brand">
        <span className="logo-icon">⚡</span>
        <span>FlagFlow</span>
        <button className="sidebar-close" aria-label="Close navigation menu" onClick={onClose} type="button">×</button>
      </div>
      <p className="sidebar-label">Workspace</p>
      <nav className="sidebar-nav">
        {primaryLinks.map((link) => (
          <NavLink
            className={({ isActive }) => `sidebar-link${isActive ? " is-active" : ""}`}
            end={link.to === "/dashboard"}
            key={link.to}
            onClick={onClose}
            to={link.to}
          >
            <span className="sidebar-icon" aria-hidden="true">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <p className="sidebar-label">Account</p>
        <NavLink className={({ isActive }) => `sidebar-link${isActive ? " is-active" : ""}`} onClick={onClose} to="/settings">
          <span className="sidebar-icon" aria-hidden="true">⌁</span>
          <span>Settings</span>
        </NavLink>
        <button className="sidebar-signout" onClick={onSignOut} type="button">
          <span className="sidebar-icon" aria-hidden="true">↪</span>
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
