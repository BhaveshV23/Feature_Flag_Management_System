import { useState } from "react";
import { login as requestLogin } from "../services/api";
import AuthContext from "./authContext";

const TOKEN_KEY = "flagflow_access_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));

  const login = async (username, password) => {
    const result = await requestLogin(username, password);
    localStorage.setItem(TOKEN_KEY, result.access_token);
    setToken(result.access_token);
    return result;
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: Boolean(token), login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

