type TelegramWebApp = {
  initData?: string;
  colorScheme?: 'light' | 'dark';
  ready?: () => void;
  expand?: () => void;
  close?: () => void;
  BackButton?: { show: () => void; hide: () => void; onClick: (handler: () => void) => void; offClick: (handler: () => void) => void };
  HapticFeedback?: { impactOccurred: (style: 'light' | 'medium' | 'heavy') => void; notificationOccurred: (type: 'success' | 'error' | 'warning') => void };
};

declare global {
  interface Window { Telegram?: { WebApp?: TelegramWebApp } }
}

export function getTelegramWebApp(): TelegramWebApp | undefined {
  return window.Telegram?.WebApp;
}

export function initTelegramShell(): void {
  const app = getTelegramWebApp();
  app?.ready?.();
  app?.expand?.();
  document.documentElement.dataset.telegramTheme = app?.colorScheme || 'light';
}

export function getTelegramInitData(): string {
  return getTelegramWebApp()?.initData || '';
}

export function bindTelegramBack(handler: () => void): () => void {
  const back = getTelegramWebApp()?.BackButton;
  if (!back) return () => undefined;
  back.show();
  back.onClick(handler);
  return () => { back.offClick(handler); back.hide(); };
}

export function haptic(type: 'light' | 'medium' = 'light'): void {
  getTelegramWebApp()?.HapticFeedback?.impactOccurred(type);
}

export function notifyHaptic(type: 'success' | 'error' | 'warning'): void {
  getTelegramWebApp()?.HapticFeedback?.notificationOccurred(type);
}
