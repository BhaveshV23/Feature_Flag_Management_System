import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import "./App.css";
import DashboardLayout from "./layouts/DashboardLayout";
import PublicLayout from "./layouts/PublicLayout";
import Dashboard from "./pages/Dashboard";
import EnvironmentsPage from "./pages/EnvironmentsPage";
import FeaturesPage from "./pages/FeaturesPage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RolloutsPage from "./pages/RolloutsPage";

const TOKEN_KEY = "flagflow_access_token";

function AppRoutes() {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)));

  const signOut = () => {
    localStorage.removeItem(TOKEN_KEY);
    setIsAuthenticated(false);
    navigate("/");
  };

  const requireAuthentication = (page) => (
    isAuthenticated ? <DashboardLayout onSignOut={signOut}>{page}</DashboardLayout> : <Navigate to="/login" replace />
  );

  return (
    <Routes>
      <Route path="/" element={<PublicLayout><LandingPage isAuthenticated={isAuthenticated} onLogin={() => navigate("/login")} onSignOut={signOut} /></PublicLayout>} />
      <Route path="/login" element={<PublicLayout><LoginPage onBack={() => navigate("/")} onLogin={() => { setIsAuthenticated(true); navigate("/dashboard"); }} /></PublicLayout>} />
      <Route path="/dashboard" element={requireAuthentication(<Dashboard />)} />
      <Route path="/features" element={requireAuthentication(<FeaturesPage />)} />
      <Route path="/environments" element={requireAuthentication(<EnvironmentsPage />)} />
      <Route path="/rollouts" element={requireAuthentication(<RolloutsPage />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
