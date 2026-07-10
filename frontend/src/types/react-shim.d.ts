declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare module 'react' {
  export type ReactNode = any;
  export class Component<P = any, S = any> {
    constructor(props: P);
    props: P;
    state: S;
    setState(state: Partial<S>): void;
    componentDidCatch?(error: Error, info: any): void;
    render(): ReactNode;
  }
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useMemo<T>(factory: () => T, deps: any[]): T;
  export function useState<T>(initial: T | (() => T)): [T, (value: T | ((current: T) => T)) => void];
}

declare module 'react/jsx-runtime' {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare module 'react-dom/client' {
  export function createRoot(element: Element | DocumentFragment): { render: (node: any) => void };
}

declare module '@tanstack/react-query' {
  export class QueryClient {
    constructor(options?: any);
  }
  export function QueryClientProvider(props: any): any;
}

declare module '@vitejs/plugin-react' {
  const react: () => any;
  export default react;
}

declare module 'vite' {
  export function defineConfig(config: any): any;
}
