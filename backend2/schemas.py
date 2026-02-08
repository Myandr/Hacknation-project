"""Pydantic-Schemas für Agentic Commerce API."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---- Filter (Größe, Preis, Farbe, Lieferzeit) ----

class FilterRequest(BaseModel):
    """Filter-Daten vom Frontend: Größe, Preis, Farbe, Lieferzeit."""
    size_clothing: str | None = None   # z.B. XS, S, M, L
    size_pants: str | None = None     # z.B. 28, 30, 32
    size_shoes: str | None = None     # z.B. 40, 41, 42
    price_min: float | None = None
    price_max: float | None = None
    color: str | None = None          # eine Farbe oder kommasepariert
    delivery_time_days: int | None = None  # max. Lieferzeit in Tagen


class FilterOut(BaseModel):
    """Gespeicherte Filter (Response)."""
    size_clothing: str | None = None
    size_pants: str | None = None
    size_shoes: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    color: str | None = None
    delivery_time_days: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ---- Brief / Requirements ----

class ShoppingSpecOut(BaseModel):
    """Strukturierter Shopping-Brief (Output)."""
    budget_min: float | None = None
    budget_max: float | None = None
    budget_currency: str | None = None
    delivery_deadline: str | None = None
    category: str | None = None
    country: str | None = None
    city: str | None = None
    event_type: str | None = None
    event_name: str | None = None
    people_count: int | None = None
    reason: str | None = None
    preferences: list[str] = []
    must_haves: list[str] = []
    nice_to_haves: list[str] = []
    is_complete: bool = False


# ---- Chat ----

class MessageRequest(BaseModel):
    message: str


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class MessageResponse(BaseModel):
    session_id: str
    reply: str
    requirements: ShoppingSpecOut
    status: str


# ---- Session ----

class SessionResponse(BaseModel):
    session_id: str
    status: str
    requirements: ShoppingSpecOut | None
    messages: list[MessageOut]
    cart: list["CartItemOut"] = []
    created_at: datetime


# ---- Produkte (Multi-Retailer) ----

class ProductVariant(BaseModel):
    size: str | None = None
    color: str | None = None
    sku: str | None = None
    extra: dict[str, Any] = {}


class ProductOut(BaseModel):
    """Ein Produkt von einem Händler (für Suche/Ranking)."""
    retailer_id: str
    product_id: str
    title: str
    price: float
    currency: str = "EUR"
    delivery_estimate_days: int | None = None
    image_url: str | None = None
    product_url: str | None = None
    variants: list[ProductVariant] = []
    raw: dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


# ---- Ranking ----

class RankedProductOut(ProductOut):
    """Produkt mit Ranking-Score und Begründung."""
    score: float
    score_breakdown: dict[str, float] = {}
    explanation: str = ""


class SearchResultOut(BaseModel):
    """Ergebnis der Multi-Retailer-Suche inkl. Ranking."""
    shopping_spec: ShoppingSpecOut
    products: list[RankedProductOut]
    ranking_explanation: str = ""
    why_first: str = ""


# ---- Cart ----

class CartItemOut(BaseModel):
    id: int
    retailer_id: str
    product_id: str
    title: str
    price: float
    currency: str = "EUR"
    delivery_estimate_days: int | None = None
    quantity: int = 1
    variant_info: dict[str, Any] = {}
    image_url: str | None = None
    product_url: str | None = None


class CartSummaryOut(BaseModel):
    """Kombinierter Warenkorb mit Summen."""
    items: list[CartItemOut]
    total_price: float
    currency: str = "EUR"
    by_retailer: dict[str, float] = {}
    delivery_summary: str = ""


# ---- Checkout (Simulation) ----

class CheckoutStepOut(BaseModel):
    """Ein simulierter Checkout-Schritt pro Händler."""
    retailer_id: str
    step_number: int
    description: str
    url: str | None = None
    status: str = "pending"  # pending | simulated_done


class CheckoutSimulationOut(BaseModel):
    """Simulierter Checkout: eine Adresse/Zahlung, Schritte pro Händler."""
    session_id: str
    payment_entered_once: bool = True
    address_entered_once: bool = True
    steps: list[CheckoutStepOut] = []
    message: str = "Checkout ist simuliert – keine echte Zahlung."


class AddToCartRequest(BaseModel):
    """Produkt (z. B. aus Suchergebnis) in den Warenkorb."""
    retailer_id: str
    product_id: str
    title: str
    price: float
    currency: str = "EUR"
    delivery_estimate_days: int | None = None
    image_url: str | None = None
    product_url: str | None = None
    variants: list[ProductVariant] = []
    quantity: int = 1


class UpdateQuantityRequest(BaseModel):
    quantity: int


# ---- Shopping-Plan (KI-Denkprozess) ----

class ShoppingPlanComponent(BaseModel):
    """Eine Position der Einkaufsliste mit Budgetaufteilung."""
    id: str
    name: str
    category: str
    budget_min: float
    budget_max: float
    priority: str = "must_have"  # must_have | nice_to_have
    quantity: int = 1
    notes: list[str] = []


class ShoppingPlanOut(BaseModel):
    """Ergebnis des KI-Denkprozesses: Einkaufsliste mit Budgetaufteilung (nur JSON-Daten)."""
    currency: str = "EUR"
    total_budget_min: float = 0.0
    total_budget_max: float = 0.0
    components: list[ShoppingPlanComponent] = []


class PlanComponentSearchOut(BaseModel):
    """Pro Plan-Komponente: Komponente + erste 3 Google-Shopping-Treffer."""
    component: ShoppingPlanComponent
    shopping_results: list[dict] = []  # Rohdaten von SerpAPI (title, link, price, ...)


# Für SessionResponse
SessionResponse.model_rebuild()
