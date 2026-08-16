import { createContext, useContext, useMemo, useState } from "react";

import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "null");
    } catch {
      return null;
    }
  });

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", {
      email,
      password,
    });

    localStorage.setItem("access_token", data.access_token);

    const profile = (await api.get("/auth/profile")).data;

    localStorage.setItem("user", JSON.stringify(profile));

    setUser(profile);

    return profile;
  };

  const register = async (payload) => {
    const { data } = await api.post("/auth/register", payload);

    return data;
  };

  const verifyEmail = async (email, code) => {
    const { data } = await api.post("/auth/verify-email", {
      email,
      code,
    });

    return data;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setUser(null);
  };

  const value = useMemo(
    () => ({
      user,
      login,
      register,
      verifyEmail,
      logout,
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
