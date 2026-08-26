import { useState } from "react";
import "./App.css";

const TOKEN_KEY = "flagflow_access_token";

const features = [
  {
    icon: "🚩",
    title: "Feature Flags",
    text: "Enable or disable features instantly without redeploying your application.",
  },
  {
    icon: "🎯",
    title: "User Targeting",
    text: "Target specific users and groups with flexible targeting rules.",
  },
  {
    icon: "📊",
    title: "Percentage Rollouts",
    text: "Gradually release features to a percentage of users.",
  },
  {
    icon: "🌍",
    title: "Environment Control",
    text: "Manage feature configurations across development, staging and production.",
  },
  {
    icon: "📜",
    title: "Audit Logs",
    text: "Track configuration changes and maintain complete release visibility.",
  },
  {
    icon: "⚡",
    title: "Fast Evaluation",
    text: "Evaluate feature flags quickly using Redis-powered caching.",
  },
];

function LoginPage({ onBack, onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to sign in.");
      }

      localStorage.setItem(TOKEN_KEY, result.access_token);
      onLogin();
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in. Check the API connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <button className="back-link" onClick={onBack} type="button">
        ← Back to FlagFlow
      </button>
      <section className="auth-panel" aria-labelledby="login-title">
        <div className="auth-brand"><span className="logo-icon">⚡</span> FlagFlow</div>
        <div className="badge">Secure workspace access</div>
        <h1 id="login-title">Welcome back.</h1>
        <p className="auth-intro">Sign in to manage releases and feature flags across your environments.</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
            placeholder="Enter your username"
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
            placeholder="Enter your password"
          />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="btn primary login-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="auth-note">Your session is protected with a short-lived bearer token.</p>
      </section>
    </main>
  );
}

function App() {
  const [page, setPage] = useState(() => (localStorage.getItem(TOKEN_KEY) ? "app" : "landing"));
  const [flags, setFlags] = useState({
    checkout: true,
    darkMode: true,
  });

  const toggleFlag = (flag) => {
    setFlags((previous) => ({
      ...previous,
      [flag]: !previous[flag],
    }));
  };

  const scrollToFeatures = () => {
    document
      .getElementById("features")
      ?.scrollIntoView({ behavior: "smooth" });
  };

  const openLogin = () => setPage("login");
  const signOut = () => {
    localStorage.removeItem(TOKEN_KEY);
    setPage("landing");
  };

  if (page === "login") {
    return <LoginPage onBack={() => setPage("landing")} onLogin={() => setPage("app")} />;
  }

  return (
    <div className="app">

      {/* Navbar */}
      <header className="navbar">
        <div className="logo">
          <span className="logo-icon">⚡</span>
          <span>FlagFlow</span>
        </div>

        <nav>
          <a href="#features">Features</a>
          <a href="#workflow">How It Works</a>
          <a href="#about">About</a>
        </nav>

        <div className="nav-buttons">
          {page === "app" ? (
            <button className="btn secondary" onClick={signOut}>Sign out</button>
          ) : (
            <button className="btn secondary" onClick={openLogin}>Login</button>
          )}

          <button className="btn primary" onClick={scrollToFeatures}>
            {page === "app" ? "Explore Workspace" : "Get Started"}
          </button>
        </div>
      </header>


      {/* Hero */}
      <section className="hero">

        <div className="hero-content">

          <div className="badge">
            <span>●</span>
            Smart Feature Management
          </div>

          <h1>
            Control Features.
            <br />
            <span>Ship With Confidence.</span>
          </h1>

          <p>
            Manage feature flags, control rollouts, target users and
            release application features safely across multiple
            environments.
          </p>

          <div className="hero-buttons">

            <button
              className="btn primary large"
              onClick={page === "app" ? scrollToFeatures : openLogin}
            >
              {page === "app" ? "Open Workspace →" : "Get Started →"}
            </button>

            <button
              className="btn secondary large"
              onClick={scrollToFeatures}
            >
              Explore Features
            </button>

          </div>

          <div className="stats">

            <div>
              <strong>99.9%</strong>
              <span>Reliable Releases</span>
            </div>

            <div>
              <strong>24/7</strong>
              <span>Feature Control</span>
            </div>

            <div>
              <strong>100%</strong>
              <span>Release Visibility</span>
            </div>

          </div>

        </div>


        {/* Dashboard Preview */}
        <div className="dashboard">

          <div className="dashboard-window">

            <div className="window-header">

              <div className="window-dots">
                <span />
                <span />
                <span />
              </div>

              <span>Feature Dashboard</span>

            </div>


            <div className="dashboard-body">

              <div className="dashboard-top">

                <div>
                  <small>Environment</small>
                  <strong>Production</strong>
                </div>

                <span className="live">● Live</span>

              </div>


              <div className="flag">

                <div className="flag-info">
                  <div className="flag-icon">🚀</div>

                  <div>
                    <strong>New Checkout</strong>
                    <small>checkout_v2</small>
                  </div>
                </div>

                <label className="switch">

                  <input
                    type="checkbox"
                    checked={flags.checkout}
                    onChange={() => toggleFlag("checkout")}
                  />

                  <span className="slider" />

                </label>

              </div>


              <div className="flag">

                <div className="flag-info">
                  <div className="flag-icon">🌙</div>

                  <div>
                    <strong>Dark Mode</strong>
                    <small>dark_mode</small>
                  </div>
                </div>

                <label className="switch">

                  <input
                    type="checkbox"
                    checked={flags.darkMode}
                    onChange={() => toggleFlag("darkMode")}
                  />

                  <span className="slider" />

                </label>

              </div>


              <div className="flag">

                <div className="flag-info">
                  <div className="flag-icon">🔍</div>

                  <div>
                    <strong>Beta Search</strong>
                    <small>beta_search</small>
                  </div>
                </div>

                <div className="percentage">
                  35%
                </div>

              </div>


              <div className="dashboard-footer">

                <span>
                  <i />
                  All systems operational
                </span>

                <span>3 active flags</span>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* Features */}
      <section className="features-section" id="features">

        <div className="section-heading">

          <div className="badge">
            Powerful Controls
          </div>

          <h2>
            Everything you need to
            <br />
            <span>release safely.</span>
          </h2>

          <p>
            Simplify feature releases with centralized controls,
            targeting, rollouts and monitoring.
          </p>

        </div>


        <div className="features-grid">

          {features.map((feature) => (

            <div className="feature-card" key={feature.title}>

              <div className="card-icon">
                {feature.icon}
              </div>

              <h3>{feature.title}</h3>

              <p>{feature.text}</p>

              <a href="#workflow">
                Learn more →
              </a>

            </div>

          ))}

        </div>

      </section>


      {/* Workflow */}
      <section className="workflow" id="workflow">

        <div className="section-heading">

          <div className="badge">
            Simple Workflow
          </div>

          <h2>
            Release in <span>four steps.</span>
          </h2>

        </div>


        <div className="steps">

          <div className="step">
            <div className="step-number">01</div>
            <h3>Create</h3>
            <p>Create a feature flag for your application.</p>
          </div>

          <div className="step-line" />

          <div className="step">
            <div className="step-number">02</div>
            <h3>Configure</h3>
            <p>Configure targeting rules and environments.</p>
          </div>

          <div className="step-line" />

          <div className="step">
            <div className="step-number">03</div>
            <h3>Roll Out</h3>
            <p>Gradually release the feature to your users.</p>
          </div>

          <div className="step-line" />

          <div className="step">
            <div className="step-number">04</div>
            <h3>Monitor</h3>
            <p>Track changes and maintain release visibility.</p>
          </div>

        </div>

      </section>


      {/* CTA */}
      <section className="cta" id="about">

        <div className="cta-box">

          <div className="cta-icon">
            ⚡
          </div>

          <h2>
            Ready to take control
            <br />
            of your releases?
          </h2>

          <p>
            Start managing features with confidence.
          </p>

          <button
            className="btn primary large"
            onClick={page === "app" ? scrollToFeatures : openLogin}
          >
            {page === "app" ? "Open Workspace →" : "Get Started →"}
          </button>

        </div>

      </section>


      {/* Footer */}
      <footer>

        <div className="footer-main">

          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span>FlagFlow</span>
          </div>

          <p>
            Feature Management & Release Control System
          </p>

          <div className="footer-links">
            <a href="#features">Features</a>
            <a href="#workflow">How It Works</a>
            <a href="#about">About</a>
          </div>

        </div>

        <div className="copyright">
          © 2026 FlagFlow. Built for safer releases.
        </div>

      </footer>

    </div>
  );
}

export default App;