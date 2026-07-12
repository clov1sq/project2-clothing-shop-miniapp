import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { ApiError, authApi } from '../shared/api/client';
import type { User } from '../shared/api/types';
import { getTelegramInitData, initTelegramShell } from '../shared/telegram/telegram';

type AuthState = {
  user: User | null;
  loading: boolean;
  error: string | null;
  retry: () => void;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    initTelegramShell();
    let cancelled = false;
    setLoading(true);
    setError(null);
    authApi.login(getTelegramInitData())
      .then(({ user: nextUser }) => { if (!cancelled) setUser(nextUser); })
      .catch((reason: unknown) => {
        if (cancelled) return;
        const message = reason instanceof ApiError ? reason.message : 'Не вдалося відкрити магазин';
        setError(message);
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [attempt]);

  const value = useMemo<AuthState>(() => ({
    user,
    loading,
    error,
    retry: () => setAttempt((current) => current + 1),
    logout: async () => { await authApi.logout(); setUser(null); },
  }), [user, loading, error]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
