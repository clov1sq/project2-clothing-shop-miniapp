import {
  Children,
  createContext,
  isValidElement,
  useContext,
  useEffect,
  useMemo,
  useState,
  type AnchorHTMLAttributes,
  type ReactElement,
  type ReactNode,
} from 'react';

type LocationState = { pathname: string; search: string };
type NavigateOptions = { replace?: boolean };
type RouteDefinition = { path: string; element: ReactNode };
type RouteProps = RouteDefinition;

type RouterState = LocationState & {
  navigate: (target: string | number, options?: NavigateOptions) => void;
};

const RouterContext = createContext<RouterState | null>(null);
const ParamsContext = createContext<Record<string, string>>({});

function readLocation(): LocationState {
  const raw = window.location.hash.replace(/^#/, '') || '/';
  const [pathnamePart, searchPart = ''] = raw.split('?');
  const pathname = pathnamePart.startsWith('/') ? pathnamePart : `/${pathnamePart}`;
  return { pathname, search: searchPart ? `?${searchPart}` : '' };
}

export function HashRouter({ children }: { children: ReactNode }) {
  const [location, setLocation] = useState<LocationState>(() => readLocation());
  useEffect(() => {
    const onChange = () => setLocation(readLocation());
    window.addEventListener('hashchange', onChange);
    return () => window.removeEventListener('hashchange', onChange);
  }, []);
  const navigate = (target: string | number, options: NavigateOptions = {}) => {
    if (typeof target === 'number') { window.history.go(target); return; }
    const nextHash = `#${target.startsWith('/') ? target : `/${target}`}`;
    if (options.replace) {
      window.history.replaceState(null, '', nextHash);
      setLocation(readLocation());
    } else {
      window.location.hash = nextHash;
    }
  };
  const value = useMemo<RouterState>(() => ({ ...location, navigate }), [location.pathname, location.search]);
  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}

export function useLocation(): LocationState {
  const context = useContext(RouterContext);
  if (!context) throw new Error('useLocation must be used inside HashRouter');
  return { pathname: context.pathname, search: context.search };
}

export function useNavigate() {
  const context = useContext(RouterContext);
  if (!context) throw new Error('useNavigate must be used inside HashRouter');
  return context.navigate;
}

export function useParams<T extends Record<string, string | undefined> = Record<string, string>>() {
  return useContext(ParamsContext) as T;
}

export function useSearchParams(): [URLSearchParams, (next: URLSearchParams | ((current: URLSearchParams) => URLSearchParams), options?: NavigateOptions) => void] {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const setParams = (nextValue: URLSearchParams | ((current: URLSearchParams) => URLSearchParams), options: NavigateOptions = {}) => {
    const next = typeof nextValue === 'function' ? nextValue(new URLSearchParams(params)) : nextValue;
    const query = next.toString();
    navigate(`${location.pathname}${query ? `?${query}` : ''}`, options);
  };
  return [params, setParams];
}

function matchPath(pattern: string, pathname: string): Record<string, string> | null {
  if (pattern === '*') return {};
  const patternParts = pattern.split('/').filter(Boolean);
  const pathParts = pathname.split('/').filter(Boolean);
  if (patternParts.length !== pathParts.length) return null;
  const params: Record<string, string> = {};
  for (let index = 0; index < patternParts.length; index += 1) {
    const expected = patternParts[index];
    const actual = pathParts[index];
    if (expected.startsWith(':')) params[expected.slice(1)] = decodeURIComponent(actual);
    else if (expected !== actual) return null;
  }
  return params;
}

export function Route(_: RouteProps) { return null; }

export function Routes({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  let fallback: ReactNode = null;
  for (const child of Children.toArray(children)) {
    if (!isValidElement<RouteProps>(child)) continue;
    if (child.props.path === '*') { fallback = child.props.element; continue; }
    const params = matchPath(child.props.path, pathname);
    if (params) return <ParamsContext.Provider value={params}>{child.props.element}</ParamsContext.Provider>;
  }
  return <>{fallback}</>;
}

export function Navigate({ to, replace = false }: { to: string; replace?: boolean }) {
  const navigate = useNavigate();
  useEffect(() => navigate(to, { replace }), [navigate, replace, to]);
  return null;
}

type LinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & { to: string };
export function Link({ to, onClick, children, ...props }: LinkProps) {
  const navigate = useNavigate();
  return <a href={`#${to}`} {...props} onClick={(event) => {
    onClick?.(event);
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(to);
  }}>{children}</a>;
}

type NavLinkProps = Omit<LinkProps, 'className'> & {
  end?: boolean;
  className?: string | ((state: { isActive: boolean }) => string);
};
export function NavLink({ to, end = false, className, ...props }: NavLinkProps) {
  const location = useLocation();
  const isActive = end ? location.pathname === to : location.pathname === to || location.pathname.startsWith(`${to}/`);
  const resolved = typeof className === 'function' ? className({ isActive }) : className;
  return <Link to={to} className={resolved} {...props}/>;
}
