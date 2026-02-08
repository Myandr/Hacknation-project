"""SQLAlchemy-Modelle für Agentic Commerce."""
import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class ShoppingSession(Base):
    """Eine Shopping-Session (Konversation + Cart + Checkout)."""
    __tablename__ = "shopping_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    status = Column(String, default="gathering_info")
    # gathering_info | ready_for_search | searching | cart_ready | checkout_simulated
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    requirements = relationship(
        "ShoppingRequirement",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    messages = relationship(
        "ConversationMessage",
        back_populates="session",
        order_by="ConversationMessage.created_at",
        cascade="all, delete-orphan",
    )
    cart_items = relationship(
        "CartItem",
        back_populates="session",
        order_by="CartItem.created_at",
        cascade="all, delete-orphan",
    )


class ShoppingRequirement(Base):
    """Strukturierte Shopping-Anforderungen (Brief)."""
    __tablename__ = "shopping_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("shopping_sessions.id"), unique=True)

    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    budget_currency = Column(String, nullable=True)
    delivery_deadline = Column(String, nullable=True)  # YYYY-MM-DD
    category = Column(String, nullable=True)  # clothing | food | both | other
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    event_type = Column(String, nullable=True)
    event_name = Column(String, nullable=True)
    people_count = Column(Integer, nullable=True)
    reason = Column(String, nullable=True)
    preferences = Column(Text, nullable=True)  # JSON array
    must_haves = Column(Text, nullable=True)
    nice_to_haves = Column(Text, nullable=True)
    is_complete = Column(Boolean, default=False)

    session = relationship("ShoppingSession", back_populates="requirements")

    def to_dict(self) -> dict:
        return {
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "budget_currency": self.budget_currency,
            "delivery_deadline": self.delivery_deadline,
            "category": self.category,
            "country": self.country,
            "city": self.city,
            "event_type": self.event_type,
            "event_name": self.event_name,
            "people_count": self.people_count,
            "reason": self.reason,
            "preferences": json.loads(self.preferences) if self.preferences else [],
            "must_haves": json.loads(self.must_haves) if self.must_haves else [],
            "nice_to_haves": json.loads(self.nice_to_haves) if self.nice_to_haves else [],
            "is_complete": self.is_complete,
        }

    def merge_update(self, data: dict) -> None:
        scalar = [
            "budget_min", "budget_max", "budget_currency", "delivery_deadline",
            "category", "country", "city", "event_type", "event_name",
            "people_count", "reason",
        ]
        list_fields = ["preferences", "must_haves", "nice_to_haves"]
        for k in scalar:
            if k in data and data[k] is not None:
                setattr(self, k, data[k])
        for k in list_fields:
            if k in data and data[k]:
                existing = json.loads(getattr(self, k) or "[]")
                for item in data[k]:
                    if item not in existing:
                        existing.append(item)
                setattr(self, k, json.dumps(existing))


class ConversationMessage(Base):
    """Eine Nachricht in der Konversation."""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("shopping_sessions.id"))
    role = Column(String)  # user | assistant
    content = Column(Text)
    created_at = Column(DateTime, default=_utcnow)

    session = relationship("ShoppingSession", back_populates="messages")


class CartItem(Base):
    """Ein Artikel im kombinierten Warenkorb (mehrere Händler)."""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("shopping_sessions.id"))
    retailer_id = Column(String, nullable=False)  # stylehub | urbanoutfit | sportdirect
    product_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    delivery_estimate_days = Column(Integer, nullable=True)
    quantity = Column(Integer, default=1)
    variant_info = Column(Text, nullable=True)  # JSON, z.B. {"size": "M", "color": "blue"}
    image_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    raw_product = Column(Text, nullable=True)  # JSON für Ersatz/Optimierung
    created_at = Column(DateTime, default=_utcnow)

    session = relationship("ShoppingSession", back_populates="cart_items")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "retailer_id": self.retailer_id,
            "product_id": self.product_id,
            "title": self.title,
            "price": self.price,
            "currency": self.currency,
            "delivery_estimate_days": self.delivery_estimate_days,
            "quantity": self.quantity,
            "variant_info": json.loads(self.variant_info) if self.variant_info else {},
            "image_url": self.image_url,
            "product_url": self.product_url,
        }


class SearchFilter(Base):
    """Globale Filter (Größe, Preis, Farbe, Lieferzeit) – ein Datensatz für die App."""
    __tablename__ = "search_filters"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Größe: Kleidung (z.B. XS, S, M, L), Hose (z.B. 28, 30), Schuhe (z.B. 40, 42)
    size_clothing = Column(String, nullable=True)
    size_pants = Column(String, nullable=True)
    size_shoes = Column(String, nullable=True)

    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    color = Column(String, nullable=True)  # eine Farbe oder kommasepariert

    delivery_time_days = Column(Integer, nullable=True)  # max. Lieferzeit in Tagen

    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    def to_dict(self) -> dict:
        return {
            "size_clothing": self.size_clothing,
            "size_pants": self.size_pants,
            "size_shoes": self.size_shoes,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "color": self.color,
            "delivery_time_days": self.delivery_time_days,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
