import { useEffect, useState } from "react";
import { login as requestLogin } from "../services/api";
import AuthContext from "./authContext";

const TOKEN_KEY = "flagflow_access_token";
const REDIRECT_KEY = "flagflow_post_auth_path";

function decodeTokenPayload(token) {
  if (!token) return false;
  const parts = token.split(".");
  if (parts.length !== 3) return false;

  try {
    const encodedPayload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = encodedPayload.padEnd(Math.ceil(encodedPayload.length / 4) * 4, "=");
    const payload = JSON.parse(atob(paddedPayload));
    return payload;
  } catch {
    return false;
  }
}

function hasValidToken(token) {
  const payload = decodeTokenPayload(token);
  return Boolean(payload && typeof payload.exp === "number" && payload.exp > Math.floor(Date.now() / 1000));
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState("User");
  const [isReady, setIsReady] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);

  useEffect(() => {
    function initializeAuthentication() {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (hasValidToken(storedToken)) {
        setToken(storedToken);
        const payload = decodeTokenPayload(storedToken);
        setUsername(typeof payload?.sub === "string" && payload.sub.trim() ? payload.sub : "User");
      } else if (storedToken) {
        localStorage.removeItem(TOKEN_KEY);
      }
      setIsReady(true);
    }
    initializeAuthentication();

    const handleInvalidToken = () => {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUsername("User");
      setSessionExpired(true);
    };
    window.addEventListener("flagflow:auth-invalid", handleInvalidToken);
    return () => window.removeEventListener("flagflow:auth-invalid", handleInvalidToken);
  }, []);

  const login = async (username, password) => {
    const result = await requestLogin(username, password);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    const payload = decodeTokenPayload(result.access_token);
    setUsername(typeof payload?.sub === "string" && payload.sub.trim() ? payload.sub : "User");
    setIsReady(true);
    setSessionExpired(false);
    return result;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUsername("User");
    setSessionExpired(false);
  };

  const consumeRedirectPath = () => {
    const destination = localStorage.getItem(REDIRECT_KEY);
    localStorage.removeItem(REDIRECT_KEY);
    return destination && destination.startsWith("/") && !destination.startsWith("//") ? destination : null;
  };

  if (!isReady) return null;

  return (
    <AuthContext.Provider value={{ token, username, sessionExpired, isAuthenticated: Boolean(token), login, logout, consumeRedirectPath }}>
      {children}
    </AuthContext.Provider>
  );
}

