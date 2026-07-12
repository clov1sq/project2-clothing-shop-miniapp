export function ProductSkeleton() {
  return (
    <article className="product-skeleton" aria-hidden="true">
      <div className="skeleton skeleton--media" />
      <div className="skeleton skeleton--line" />
      <div className="skeleton skeleton--line skeleton--short" />
    </article>
  );
}

export function HomeSkeleton() {
  return (
    <main className="auth-loading-shell" aria-label="Завантаження магазину">
      <div className="auth-loading-shell__brand skeleton" />
      <div className="auth-loading-shell__hero skeleton" />
      <div className="auth-loading-shell__chips">
        {Array.from({ length: 4 }).map((_, index) => <span className="skeleton" key={index} />)}
      </div>
      <div className="product-grid">
        {Array.from({ length: 4 }).map((_, index) => <ProductSkeleton key={index} />)}
      </div>
    </main>
  );
}
