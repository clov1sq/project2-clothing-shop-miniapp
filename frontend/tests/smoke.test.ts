import { readRouteFromHash } from '../src/app/routes';

// Placeholder frontend test target. Real component tests start when UI modules become functional.
if (typeof window !== 'undefined') {
  window.location.hash = '#/unknown';
  readRouteFromHash();
}
