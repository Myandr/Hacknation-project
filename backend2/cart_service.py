"""Kombinierter Warenkorb: mehrere Händler, Summen, Ersetzen/Entfernen."""
import json
from sqlalchemy.orm import Session

from models import CartItem, ShoppingSession
from schemas import CartItemOut, CartSummaryOut
from retailers.base import RetailerProduct


def cart_to_summary(session: ShoppingSession) -> CartSummaryOut:
    """Erstellt CartSummaryOut aus der Session."""
    items = [CartItemOut(**item.to_dict()) for item in session.cart_items]
    total = sum(i.price * i.quantity for i in session.cart_items)
    by_retailer: dict[str, float] = {}
    for i in session.cart_items:
        by_retailer[i.retailer_id] = by_retailer.get(i.retailer_id, 0) + i.price * i.quantity
    delivery_days = [i.delivery_estimate_days for i in session.cart_items if i.delivery_estimate_days is not None]
    delivery_summary = f"Max. {max(delivery_days)} Tage" if delivery_days else "Variabel"
    return CartSummaryOut(
        items=items,
        total_price=round(total, 2),
        currency=session.cart_items[0].currency if session.cart_items else "EUR",
        by_retailer=by_retailer,
        delivery_summary=delivery_summary,
    )


def add_to_cart(db: Session, session_id: str, product: RetailerProduct, quantity: int = 1, variant_info: dict | None = None) -> CartItem | None:
    """Fügt ein Produkt zum Warenkorb hinzu."""
    session = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not session:
        return None
    item = CartItem(
        session_id=session_id,
        retailer_id=product.retailer_id,
        product_id=product.product_id,
        title=product.title,
        price=product.price,
        currency=product.currency,
        delivery_estimate_days=product.delivery_estimate_days,
        quantity=quantity,
        variant_info=json.dumps(variant_info or {}),
        image_url=product.image_url,
        product_url=product.product_url,
        raw_product=json.dumps(product.raw) if product.raw else None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_cart(db: Session, session_id: str, cart_item_id: int) -> bool:
    """Entfernt einen Eintrag aus dem Warenkorb."""
    item = db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.id == cart_item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def update_cart_item_quantity(db: Session, session_id: str, cart_item_id: int, quantity: int) -> bool:
    """Aktualisiert die Menge eines Cart-Items."""
    if quantity < 1:
        return remove_from_cart(db, session_id, cart_item_id)
    item = db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.id == cart_item_id).first()
    if not item:
        return False
    item.quantity = quantity
    db.commit()
    return True


def replace_cart_item(
    db: Session,
    session_id: str,
    cart_item_id: int,
    new_product: RetailerProduct,
    quantity: int = 1,
) -> bool:
    """Ersetzt ein Cart-Item durch ein anderes Produkt."""
    item = db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.id == cart_item_id).first()
    if not item:
        return False
    item.retailer_id = new_product.retailer_id
    item.product_id = new_product.product_id
    item.title = new_product.title
    item.price = new_product.price
    item.currency = new_product.currency
    item.delivery_estimate_days = new_product.delivery_estimate_days
    item.quantity = quantity
    item.image_url = new_product.image_url
    item.product_url = new_product.product_url
    item.raw_product = json.dumps(new_product.raw) if new_product.raw else None
    db.commit()
    return True


def clear_cart(db: Session, session_id: str) -> int:
    """Leert den Warenkorb; gibt Anzahl gelöschter Items zurück."""
    deleted = db.query(CartItem).filter(CartItem.session_id == session_id).delete()
    db.commit()
    return deleted
