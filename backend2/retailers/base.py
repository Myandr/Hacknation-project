"""Basis-Datenstruktur und Aggregation für alle Händler."""
from dataclasses import dataclass
from typing import Any, Callable

from schemas import ProductOut, ProductVariant


@dataclass
class RetailerProduct:
    """Einheitliches Produktformat (intern)."""
    retailer_id: str
    product_id: str
    title: str
    price: float
    currency: str
    delivery_estimate_days: int | None
    image_url: str | None
    product_url: str | None
    variants: list[ProductVariant]
    raw: dict

    def to_product_out(self) -> ProductOut:
        return ProductOut(
            retailer_id=self.retailer_id,
            product_id=self.product_id,
            title=self.title,
            price=self.price,
            currency=self.currency,
            delivery_estimate_days=self.delivery_estimate_days,
            image_url=self.image_url,
            product_url=self.product_url,
            variants=self.variants,
            raw=self.raw,
        )


def search_all_retailers(
    retailers: list[tuple[str, Callable, str]],
    query: str,
    category: str | None = None,
    limit_per_retailer: int = 10,
    spec: Any = None,
) -> list[RetailerProduct]:
    """Ruft jeden Händler auf und sammelt Produkte. spec = KI-Brief für country/currency (ASOS)."""
    from schemas import ShoppingSpecOut

    results: list[RetailerProduct] = []
    for retailer_id, search_fn, _ in retailers:
        try:
            if retailer_id == "asos" and spec is not None and isinstance(spec, ShoppingSpecOut):
                products = search_fn(
                    query=query,
                    category=category,
                    limit=limit_per_retailer,
                    country=getattr(spec, "country", None),
                    currency=getattr(spec, "budget_currency", None),
                )
            else:
                products = search_fn(query=query, category=category, limit=limit_per_retailer)
            results.extend(products)
        except Exception:
            continue
    return results
