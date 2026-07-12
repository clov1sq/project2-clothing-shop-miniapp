export type TelegramUser = {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
};

type TelegramWebApp = {
  ready: () => void;
  expand: () => void;
  colorScheme?: 'light' | 'dark';
  themeParams?: Record<string, string>;
  initDataUnsafe?: { user?: TelegramUser };
  HapticFeedback?: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
  };
  BackButton?: {
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
  };
};

declare global {
  interface Window {
    Telegram?: { WebApp?: TelegramWebApp };
  }
}

export function getTelegramWebApp(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null;
}

export function getTelegramUser(): TelegramUser | null {
  return getTelegramWebApp()?.initDataUnsafe?.user ?? null;
}

export function hapticTap(): void {
  getTelegramWebApp()?.HapticFeedback?.impactOccurred('light');
}

export function initTelegramShell(): void {
  const webApp = getTelegramWebApp();
  if (webApp?.colorScheme) {
    document.documentElement.dataset.telegramTheme = webApp.colorScheme;
  }
  webApp?.ready();
  webApp?.expand();
}
