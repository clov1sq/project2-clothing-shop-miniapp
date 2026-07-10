export function CatalogPage() {
  return (
    <main className="page">
      <header className="page-header">
        <p className="eyebrow">Каталог</p>
        <h1>Товари скоро зʼявляться</h1>
      </header>
      <div className="product-grid" aria-label="Скелетон каталогу">
        {Array.from({ length: 4 }).map((_, index) => (
          <article className="product-card product-card--skeleton" key={index}>
            <div className="product-card__image" />
            <div className="product-card__line" />
            <div className="product-card__line product-card__line--short" />
          </article>
        ))}
      </div>
    </main>
  );
}
