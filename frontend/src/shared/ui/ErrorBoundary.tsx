import { Component, type ReactNode } from 'react';

type Props = { children: ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  componentDidCatch(): void {
    this.setState({ hasError: true });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="screen-state screen-state--error">
          <h1>Щось пішло не так</h1>
          <p>Оновіть Mini App або спробуйте ще раз.</p>
        </main>
      );
    }
    return this.props.children;
  }
}
