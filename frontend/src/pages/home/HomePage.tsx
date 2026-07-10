type Props = {
  shopName: string;
};

export function HomePage({ shopName }: Props) {
  return (
    <main className="page page--home">
      <section className="hero-card">
        <p className="eyebrow">Telegram Mini App</p>
        <h1>{shopName}</h1>
        <p>Чистий foundation нового fashion-магазину. Каталог і товари будуть додані у наступних версіях.</p>
      </section>
      <section className="content-card skeleton-block" aria-label="Місце для майбутніх промо-блоків">
        <span />
        <span />
        <span />
      </section>
    </main>
  );
}
