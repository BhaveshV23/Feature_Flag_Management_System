import { useState } from "react";
import "../App.css";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";

const features = [
  { icon: "🚩", title: "Feature Flags", text: "Enable or disable features instantly without redeploying your application." },
  { icon: "🎯", title: "User Targeting", text: "Target specific users and groups with flexible targeting rules." },
  { icon: "📊", title: "Percentage Rollouts", text: "Gradually release features to a percentage of users." },
  { icon: "🌍", title: "Environment Control", text: "Manage feature configurations across development, staging and production." },
  { icon: "📜", title: "Audit Logs", text: "Track configuration changes and maintain complete release visibility." },
  { icon: "⚡", title: "Fast Evaluation", text: "Evaluate feature flags quickly using Redis-powered caching." },
];

function LandingPage({ isAuthenticated, onLogin, onDashboard, onSignOut }) {
  const [flags, setFlags] = useState({ checkout: true, darkMode: true });

  const toggleFlag = (flag) => {
    setFlags((previous) => ({ ...previous, [flag]: !previous[flag] }));
  };

  const scrollToFeatures = () => {
    document.getElementById("features")?.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="app">
      <Navbar isAuthenticated={isAuthenticated} onLogin={onLogin} onSignOut={onSignOut} onSectionNavigate={scrollToSection} />

      <section className="hero">
        <div className="hero-content">
          <div className="badge"><span>●</span> Smart Feature Management</div>
          <h1>Control Features.<br /><span>Ship With Confidence.</span></h1>
          <p>Manage feature flags, control rollouts, target users and release application features safely across multiple environments.</p>
          <div className="hero-buttons">
            <button className="btn primary large" onClick={isAuthenticated ? onDashboard : onLogin}>{isAuthenticated ? "Go to Dashboard →" : "Get Started →"}</button>
            <button className="btn secondary large" onClick={scrollToFeatures}>Explore Features</button>
          </div>
          <div className="stats">
            <div><strong>99.9%</strong><span>Reliable Releases</span></div>
            <div><strong>24/7</strong><span>Feature Control</span></div>
            <div><strong>100%</strong><span>Release Visibility</span></div>
          </div>
        </div>

        <div className="dashboard">
          <div className="dashboard-window">
            <div className="window-header"><div className="window-dots"><span /><span /><span /></div><span>Feature Dashboard</span></div>
            <div className="dashboard-body">
              <div className="dashboard-top"><div><small>Environment</small><strong>Production</strong></div><span className="live">● Live</span></div>
              <div className="flag"><div className="flag-info"><div className="flag-icon">🚀</div><div><strong>New Checkout</strong><small>checkout_v2</small></div></div><label className="switch"><input type="checkbox" checked={flags.checkout} onChange={() => toggleFlag("checkout")} /><span className="slider" /></label></div>
              <div className="flag"><div className="flag-info"><div className="flag-icon">🌙</div><div><strong>Dark Mode</strong><small>dark_mode</small></div></div><label className="switch"><input type="checkbox" checked={flags.darkMode} onChange={() => toggleFlag("darkMode")} /><span className="slider" /></label></div>
              <div className="flag"><div className="flag-info"><div className="flag-icon">🔍</div><div><strong>Beta Search</strong><small>beta_search</small></div></div><div className="percentage">35%</div></div>
              <div className="dashboard-footer"><span><i />All systems operational</span><span>3 active flags</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="features-section" id="features">
        <div className="section-heading"><div className="badge">Powerful Controls</div><h2>Everything you need to<br /><span>release safely.</span></h2><p>Simplify feature releases with centralized controls, targeting, rollouts and monitoring.</p></div>
        <div className="features-grid">{features.map((feature) => <div className="feature-card" key={feature.title}><div className="card-icon">{feature.icon}</div><h3>{feature.title}</h3><p>{feature.text}</p><a href="#workflow">Learn more →</a></div>)}</div>
      </section>

      <section className="workflow" id="workflow">
        <div className="section-heading"><div className="badge">Simple Workflow</div><h2>Release in <span>four steps.</span></h2></div>
        <div className="steps">
          <div className="step"><div className="step-number">01</div><h3>Create</h3><p>Create a feature flag for your application.</p></div><div className="step-line" />
          <div className="step"><div className="step-number">02</div><h3>Configure</h3><p>Configure targeting rules and environments.</p></div><div className="step-line" />
          <div className="step"><div className="step-number">03</div><h3>Roll Out</h3><p>Gradually release the feature to your users.</p></div><div className="step-line" />
          <div className="step"><div className="step-number">04</div><h3>Monitor</h3><p>Track changes and maintain release visibility.</p></div>
        </div>
      </section>

      <section className="cta" id="about"><div className="cta-box"><div className="cta-icon">⚡</div><h2>Ready to take control<br />of your releases?</h2><p>Start managing features with confidence.</p><button className="btn primary large" onClick={onLogin}>Get Started →</button></div></section>
      <Footer />
    </div>
  );
}

export default LandingPage;
