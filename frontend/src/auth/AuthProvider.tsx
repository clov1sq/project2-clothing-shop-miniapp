import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

import { ApiError, authApi, setSessionRefreshHandler } from '../shared/api/client';
import type { User } from '../shared/api/types';
import { getTelegramInitData, initTelegramShell } from '../shared/telegram/telegram';

export type AuthStatus = 'authenticating' | 'authenticated' | 'error';

type AuthState = {
  user: User | null;
  status: AuthStatus;
  loading: boolean;
  error: string | null;
  retry: () => void;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>('authenticating');
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  const establishSession = useCallback(async (): Promise<User> => {
    await authApi.login(getTelegramInitData());
    const result = await authApi.me();
    return result.user;
  }, []);

  useEffect(() => {
    initTelegramShell();
    let cancelled = false;
    setStatus('authenticating');
    setError(null);

    establishSession()
      .then((nextUser) => {
        if (cancelled) return;
        setUser(nextUser);
        setStatus('authenticated');
      })
      .catch((reason: unknown) => {
        if (cancelled) return;
        const message =
          reason instanceof ApiError ? reason.message : 'Не вдалося відкрити магазин';
        setUser(null);
        setError(message);
        setStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [attempt, establishSession]);

  useEffect(
    () =>
      setSessionRefreshHandler(async () => {
        const nextUser = await establishSession();
        setUser(nextUser);
        setError(null);
        setStatus('authenticated');
      }),
    [establishSession],
  );

  const value = useMemo<AuthState>(
    () => ({
      user,
      status,
      loading: status === 'authenticating',
      error,
      retry: () => setAttempt((current) => current + 1),
      logout: async () => {
        await authApi.logout();
        setUser(null);
        setError('Сесію завершено');
        setStatus('error');
      },
    }),
    [user, status, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
