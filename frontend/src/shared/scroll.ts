export function getAppScrollContainer(): HTMLElement | null {
  const explicit = document.querySelector<HTMLElement>('[data-scroll-container="true"]');
  if (explicit && explicit.scrollHeight > explicit.clientHeight) return explicit;
  return document.scrollingElement as HTMLElement | null;
}

export function readScrollTop(): number {
  const container = getAppScrollContainer();
  return container?.scrollTop ?? window.scrollY;
}

export function scrollAppTo(top: number, behavior: ScrollBehavior = 'auto'): void {
  const container = getAppScrollContainer();
  if (container && container !== document.documentElement && container !== document.body) {
    container.scrollTo({ top, behavior });
    return;
  }
  window.scrollTo({ top, behavior });
}
