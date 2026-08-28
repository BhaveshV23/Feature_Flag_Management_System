import { useEffect, useState } from "react";
import { login as requestLogin } from "../services/api";
import AuthContext from "./authContext";

const TOKEN_KEY = "flagflow_access_token";

function hasValidToken(token) {
  if (!token) return false;
  const parts = token.split(".");
  if (parts.length !== 3) return false;

  try {
    const encodedPayload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = encodedPayload.padEnd(Math.ceil(encodedPayload.length / 4) * 4, "=");
    const payload = JSON.parse(atob(paddedPayload));
    return typeof payload.exp === "number" && payload.exp > Math.floor(Date.now() / 1000);
  } catch {
    return false;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    function initializeAuthentication() {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (hasValidToken(storedToken)) {
        setToken(storedToken);
      } else if (storedToken) {
        localStorage.removeItem(TOKEN_KEY);
      }
      setIsReady(true);
    }
    initializeAuthentication();

    const handleInvalidToken = () => {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
    };
    window.addEventListener("flagflow:auth-invalid", handleInvalidToken);
    return () => window.removeEventListener("flagflow:auth-invalid", handleInvalidToken);
  }, []);

  const login = async (username, password) => {
    const result = await requestLogin(username, password);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    setIsReady(true);
    return result;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };

  if (!isReady) return null;

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: Boolean(token), login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

