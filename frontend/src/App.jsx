import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import "./App.css";
import DashboardLayout from "./layouts/DashboardLayout";
import PublicLayout from "./layouts/PublicLayout";
import Dashboard from "./pages/Dashboard";
import EnvironmentsPage from "./pages/EnvironmentsPage";
import AuditLogsPage from "./pages/AuditLogsPage";
import FeaturesPage from "./pages/FeaturesPage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RolloutsPage from "./pages/RolloutsPage";
import useAuth from "./hooks/useAuth";

function AppRoutes() {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  const signOut = () => {
    logout();
    window.location.replace("/");
  };

  return (
    <Routes>
      <Route path="/" element={<PublicLayout><LandingPage isAuthenticated={isAuthenticated} onLogin={() => navigate("/login")} onSignOut={signOut} /></PublicLayout>} />
      <Route path="/login" element={<PublicLayout><LoginPage onBack={() => navigate("/")} onLogin={() => navigate("/dashboard")} /></PublicLayout>} />
      <Route element={isAuthenticated ? <DashboardLayout onSignOut={signOut} /> : <Navigate to="/login" replace />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/features" element={<FeaturesPage />} />
        <Route path="/environments" element={<EnvironmentsPage />} />
        <Route path="/rollouts" element={<RolloutsPage />} />
        <Route path="/analytics" element={<PlaceholderPage title="Analytics" />} />
        <Route path="/audit-logs" element={<AuditLogsPage />} />
        <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function PlaceholderPage({ title }) {
  return <section className="dashboard-placeholder"><p className="dashboard-eyebrow">Coming next</p><h2>{title}</h2><p>This workspace is reserved for a future dashboard module.</p></section>;
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
