import React, { createContext, useContext, useEffect, useState } from 'react';
import {
  getAuthToken,
  getMe,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from '../api';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    organization_name?: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(getAuthToken());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const storedToken = getAuthToken();
      if (!storedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const profile = await getMe();
        setUser(profile);
      } catch (err) {
        console.warn('Failed to load user session', err);
        apiLogout();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    loadUser();

    const handleExpired = () => {
      setToken(null);
      setUser(null);
    };

    window.addEventListener('triage_auth_expired', handleExpired);
    return () =>
      window.removeEventListener('triage_auth_expired', handleExpired);
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    const res = await apiLogin(credentials);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (data: {
    email: string;
    password: string;
    full_name: string;
    organization_name?: string;
  }) => {
    const res = await apiRegister(data);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    apiLogout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, isLoading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
