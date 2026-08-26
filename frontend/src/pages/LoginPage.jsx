import { useState } from "react";
import "../App.css";
import { login } from "../services/api";

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
      const result = await login(username, password);
      localStorage.setItem("flagflow_access_token", result.access_token);
      onLogin();
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in. Check the API connection.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <button className="back-link" onClick={onBack} type="button">← Back to FlagFlow</button>
      <section className="auth-panel" aria-labelledby="login-title">
        <div className="auth-brand"><span className="logo-icon">⚡</span> FlagFlow</div>
        <div className="badge">Secure workspace access</div>
        <h1 id="login-title">Welcome back.</h1>
        <p className="auth-intro">Sign in to manage releases and feature flags across your environments.</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input id="username" name="username" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" required placeholder="Enter your username" />
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required placeholder="Enter your password" />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="btn primary login-submit" disabled={isSubmitting} type="submit">{isSubmitting ? "Signing in..." : "Sign in"}</button>
        </form>
        <p className="auth-note">Your session is protected with a short-lived bearer token.</p>
      </section>
    </main>
  );
}

export default LoginPage;
