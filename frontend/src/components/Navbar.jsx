import { useState } from "react";

function Navbar({ isAuthenticated, onLogin, onSignOut, onSectionNavigate }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navigateToSection = (sectionId) => {
    onSectionNavigate(sectionId);
    setIsMenuOpen(false);
  };

  return (
    <header className="navbar">
      <div className="logo"><span className="logo-icon">⚡</span><span>FlagFlow</span></div>
      <button
        className="menu-toggle"
        aria-expanded={isMenuOpen}
        aria-label="Toggle navigation menu"
        onClick={() => setIsMenuOpen((open) => !open)}
        type="button"
      >
        <span /><span /><span />
      </button>
      <nav className={isMenuOpen ? "is-open" : ""}>
        <button onClick={() => navigateToSection("features")} type="button">Features</button>
        <button onClick={() => navigateToSection("workflow")} type="button">How It Works</button>
        <button onClick={() => navigateToSection("about")} type="button">About</button>
        <button className="mobile-login-link" onClick={() => { onLogin(); setIsMenuOpen(false); }} type="button">Login</button>
      </nav>
      <div className="nav-buttons">
        {isAuthenticated ? <button className="btn secondary" onClick={onSignOut}>Sign out</button> : <button className="btn secondary" onClick={onLogin}>Login</button>}
      </div>
    </header>
  );
}

export default Navbar;
