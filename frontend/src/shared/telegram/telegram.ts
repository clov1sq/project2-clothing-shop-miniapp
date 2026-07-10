type TelegramWebApp = {
  ready: () => void;
  expand: () => void;
  BackButton?: {
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
  };
  MainButton?: {
    setText: (text: string) => void;
    show: () => void;
    hide: () => void;
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

export function initTelegramShell(): void {
  const webApp = getTelegramWebApp();
  webApp?.ready();
  webApp?.expand();
}
