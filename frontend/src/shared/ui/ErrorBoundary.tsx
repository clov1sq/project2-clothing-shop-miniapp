import { Component, type ReactNode } from 'react';
import { AuthErrorScreen } from './AuthScreens';

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  componentDidCatch(): void {
    this.setState({ hasError: true });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return <AuthErrorScreen onRetry={() => window.location.reload()} />;
    }
    return this.props.children;
  }
}
