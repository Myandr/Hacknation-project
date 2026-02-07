import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


def _utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Shopping Session – eine Konversation / ein Shopping-Vorgang
# ---------------------------------------------------------------------------
class ShoppingSession(Base):
    __tablename__ = "shopping_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    status = Column(String, default="gathering_info")  # gathering_info | ready_for_search | searching | done
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


# ---------------------------------------------------------------------------
# Shopping Requirement – alle extrahierten Anforderungen
# ---------------------------------------------------------------------------
class ShoppingRequirement(Base):
    __tablename__ = "shopping_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("shopping_sessions.id"), unique=True)

    # Budget
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    budget_currency = Column(String, nullable=True)

    # Lieferung
    delivery_deadline = Column(String, nullable=True)

    # Kategorie
    category = Column(String, nullable=True)  # clothing | food | both | other

    # Location
    country = Column(String, nullable=True)  # z.B. "Germany", "USA"
    city = Column(String, nullable=True)  # z.B. "Berlin", "Munich"

    # Event / Anlass
    event_type = Column(String, nullable=True)
    event_name = Column(String, nullable=True)
    people_count = Column(Integer, nullable=True)
    reason = Column(String, nullable=True)

    # Wünsche  (als JSON-Arrays gespeichert)
    preferences = Column(Text, nullable=True)
    must_haves = Column(Text, nullable=True)
    nice_to_haves = Column(Text, nullable=True)

    is_complete = Column(Boolean, default=False)

    session = relationship("ShoppingSession", back_populates="requirements")

    # -- Hilfsmethoden --------------------------------------------------------

    def to_dict(self) -> dict:
        """Gibt den aktuellen Stand als Dict zurück (für den AI-Kontext)."""
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
        """Aktualisiert Felder.  Listen-Felder werden gemerged (neue Einträge
        werden angehängt), skalare Felder überschrieben."""
        _SCALAR_FIELDS = [
            "budget_min", "budget_max", "budget_currency",
            "delivery_deadline", "category", "country", "city",
            "event_type", "event_name", "people_count", "reason",
        ]
        _LIST_FIELDS = ["preferences", "must_haves", "nice_to_haves"]

        for field in _SCALAR_FIELDS:
            if field in data and data[field] is not None:
                setattr(self, field, data[field])

        for field in _LIST_FIELDS:
            if field in data and data[field]:
                existing = json.loads(getattr(self, field) or "[]")
                for item in data[field]:
                    if item not in existing:
                        existing.append(item)
                setattr(self, field, json.dumps(existing))


# ---------------------------------------------------------------------------
# Conversation Message – jede Nachricht in der Konversation
# ---------------------------------------------------------------------------
class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("shopping_sessions.id"))
    role = Column(String)  # user | assistant
    content = Column(Text)
    created_at = Column(DateTime, default=_utcnow)

    session = relationship("ShoppingSession", back_populates="messages")


