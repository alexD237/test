import { createContext, useContext, useState } from "react";
import client, { tokens } from "../api/client";

const AuthContext = createContext(null);

function decode(access) {
  if (!access) return null;
  try {
    const payload = JSON.parse(atob(access.split(".")[1]));
    return { nom_complet: payload.nom_complet, role: payload.role };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => decode(tokens.access));

  async function login(username, password) {
    const { data } = await client.post("/auth/login/", { username, password });
    tokens.set(data);
    setUser(decode(data.access));
  }

  function logout() {
    tokens.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
