from decimal import Decimal

from app.catalog.service import discount_percent, money, slugify


def test_price_helpers() -> None:
    assert money(Decimal("12")) == "12.00"
    assert discount_percent(Decimal("800"), Decimal("1000")) == 20
    assert discount_percent(Decimal("1000"), Decimal("1000")) is None


def test_slugify_is_deterministic() -> None:
    assert slugify("Пальто New 2026") == "palto-new-2026"
