import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Rork SDK Verbindungskonfiguration
const BRIDGE_URL = 'http://100.79.19.27:49152'; // Tailscale IP
const AUTH_TOKEN = 'rork-bridge-2026';

const AuthContext = createContext({
  isAuth: false,
  checkConnection: async () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [isAuth, setIsAuth] = useState(false);

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${BRIDGE_URL}/health`, {
        headers: { Authorization: `Bearer ${AUTH_TOKEN}` },
        timeout: 2000,
      });
      setIsAuth(response.status === 200);
      return response.status === 200;
    } catch {
      setIsAuth(false);
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ isAuth, checkConnection }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
