"""
Agentic Commerce API – FastAPI Backend.
Konversationeller Brief, Multi-Händler-Suche, Ranking, kombinierter Warenkorb, simulierter Checkout.
"""
import json
from datetime import date, timedelta
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import ShoppingSession, ShoppingRequirement, ConversationMessage, CartItem, SearchFilter
from schemas import (
    MessageRequest,
    MessageResponse,
    SessionResponse,
    MessageOut,
    ShoppingSpecOut,
    CartItemOut,
    CartSummaryOut,
    SearchResultOut,
    CheckoutSimulationOut,
    ShoppingPlanOut,
    ShoppingPlanComponent,
    PlanComponentSearchOut,
    AddToCartRequest,
    UpdateQuantityRequest,
    FilterRequest,
    FilterOut,
)
from agent import process_message
from shopping_planner import run_shopping_plan
from google_shopping_api import plan_and_search
from search_service import run_search
from cart_service import cart_to_summary, add_to_cart, remove_from_cart, update_cart_item_quantity
from checkout_simulation import run_checkout_simulation
from retailers.base import RetailerProduct

# Tabellen anlegen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic Commerce API",
    description="Konversationeller Einkauf: Brief erfassen, Multi-Händler-Suche, Ranking, kombinierter Warenkorb, simulierter Checkout",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _requirements_out(req: ShoppingRequirement | None) -> ShoppingSpecOut:
    if req is None:
        return ShoppingSpecOut()
    return ShoppingSpecOut(**req.to_dict())


def _get_session(session_id: str, db: Session) -> ShoppingSession:
    session = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    return session


# ---- Routes ----

@app.get("/")
def root():
    return {"message": "Agentic Commerce API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


def _apply_global_filters_to_requirement(req: ShoppingRequirement, db: Session) -> None:
    """Globale Filter als Default in die ShoppingRequirement übernehmen."""
    f = db.query(SearchFilter).first()
    if not f:
        return
    if f.price_min is not None:
        req.budget_min = f.price_min
    if f.price_max is not None:
        req.budget_max = f.price_max
    if f.delivery_time_days is not None:
        req.delivery_deadline = (date.today() + timedelta(days=f.delivery_time_days)).strftime("%Y-%m-%d")
    prefs = []
    if f.color:
        prefs.append(f"Farbe: {f.color.strip()}")
    if f.size_clothing:
        prefs.append(f"Größe Kleidung: {f.size_clothing.strip()}")
    if f.size_pants:
        prefs.append(f"Größe Hose: {f.size_pants.strip()}")
    if f.size_shoes:
        prefs.append(f"Größe Schuhe: {f.size_shoes.strip()}")
    if prefs:
        req.preferences = json.dumps(prefs)


@app.post("/sessions", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    """Neue Shopping-Session anlegen (Brief + Cart). Globale Filter werden als Default übernommen."""
    session = ShoppingSession()
    req = ShoppingRequirement(session_id=session.id)
    _apply_global_filters_to_requirement(req, db)
    session.requirements = req
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        requirements=_requirements_out(session.requirements),
        messages=[],
        cart=[],
        created_at=session.created_at,
    )


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Session inkl. Nachrichten und Warenkorb abrufen."""
    session = _get_session(session_id, db)
    cart = [CartItemOut(**i.to_dict()) for i in session.cart_items]
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        requirements=_requirements_out(session.requirements),
        messages=[MessageOut(role=m.role, content=m.content, created_at=m.created_at) for m in session.messages],
        cart=cart,
        created_at=session.created_at,
    )


@app.post("/sessions/{session_id}/chat", response_model=MessageResponse)
def chat(session_id: str, body: MessageRequest, db: Session = Depends(get_db)):
    """Nutzer-Nachricht senden; Agent antwortet und aktualisiert den Brief."""
    session = _get_session(session_id, db)
    if session.status == "ready_for_search":
        raise HTTPException(status_code=400, detail="Brief ist bereits vollständig. Starte die Suche.")

    user_msg = ConversationMessage(session_id=session.id, role="user", content=body.message)
    db.add(user_msg)
    db.commit()

    conversation = [{"role": m.role, "content": m.content} for m in session.messages]
    current_reqs = session.requirements.to_dict() if session.requirements else None
    assistant_text, tool_calls = process_message(conversation, current_reqs)

    req = session.requirements
    for tc in tool_calls:
        if tc["name"] == "update_shopping_requirements":
            req.merge_update(tc.get("arguments", {}))
        elif tc["name"] == "mark_requirements_complete":
            req.is_complete = True
            session.status = "ready_for_search"
    if req:
        db.add(req)
        db.add(session)

    assistant_msg = ConversationMessage(session_id=session.id, role="assistant", content=assistant_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(session)

    return MessageResponse(
        session_id=session.id,
        reply=assistant_text,
        requirements=_requirements_out(session.requirements),
        status=session.status,
    )


@app.post("/sessions/{session_id}/shopping-plan", response_model=ShoppingPlanOut)
def create_shopping_plan(session_id: str, db: Session = Depends(get_db)):
    """KI-Denkprozess: Aus den in der Session gesammelten Daten eine Einkaufsliste mit Budgetaufteilung erzeugen (nur JSON)."""
    session = _get_session(session_id, db)
    req = session.requirements
    if not req:
        raise HTTPException(status_code=400, detail="Session hat keine Anforderungen.")
    requirements = req.to_dict()
    plan = run_shopping_plan(requirements)
    if not plan:
        raise HTTPException(
            status_code=503,
            detail="Plan konnte nicht erstellt werden (KI oder GOOGLE_API_KEY fehlt).",
        )
    return ShoppingPlanOut(**plan)


@app.post("/sessions/{session_id}/shopping-plan/google-shopping", response_model=list[PlanComponentSearchOut])
def shopping_plan_google_search(session_id: str, db: Session = Depends(get_db)):
    """KI-Plan aus Session-Anforderungen, pro Komponente Google-Shopping-Suche (q=Name), je 3 Treffer."""
    session = _get_session(session_id, db)
    req = session.requirements
    if not req:
        raise HTTPException(status_code=400, detail="Session hat keine Anforderungen.")
    results = plan_and_search(req.to_dict(), location="Germany")
    if results is None:
        raise HTTPException(
            status_code=503,
            detail="Plan konnte nicht erstellt werden (KI oder GOOGLE_API_KEY fehlt).",
        )
    return [
        PlanComponentSearchOut(
            component=ShoppingPlanComponent(**item["component"]),
            shopping_results=item["shopping_results"],
        )
        for item in results
    ]


@app.post("/sessions/{session_id}/search", response_model=SearchResultOut)
def search(session_id: str, db: Session = Depends(get_db)):
    """Multi-Händler-Suche + Ranking basierend auf dem gespeicherten Brief."""
    session = _get_session(session_id, db)
    if session.status != "ready_for_search":
        raise HTTPException(status_code=400, detail="Brief noch nicht abgeschlossen. Chat zuerst nutzen.")
    spec = ShoppingSpecOut(**(session.requirements.to_dict()))
    session.status = "searching"
    db.commit()
    result = run_search(spec)
    return result


@app.get("/filters", response_model=FilterOut)
def get_filters(db: Session = Depends(get_db)):
    """Globale Filter (Größe, Preis, Farbe, Lieferzeit) abrufen."""
    f = db.query(SearchFilter).first()
    if not f:
        return FilterOut()
    return FilterOut(**f.to_dict())


@app.post("/filters", response_model=FilterOut)
def save_filters(body: FilterRequest, db: Session = Depends(get_db)):
    """Filter vom Frontend global speichern: Größe (Kleidung/Hose/Schuhe), Preis min/max, Farbe, Lieferzeit."""
    f = db.query(SearchFilter).first()
    if f:
        f.size_clothing = body.size_clothing if body.size_clothing is not None else f.size_clothing
        f.size_pants = body.size_pants if body.size_pants is not None else f.size_pants
        f.size_shoes = body.size_shoes if body.size_shoes is not None else f.size_shoes
        f.price_min = body.price_min if body.price_min is not None else f.price_min
        f.price_max = body.price_max if body.price_max is not None else f.price_max
        f.color = body.color if body.color is not None else f.color
        f.delivery_time_days = body.delivery_time_days if body.delivery_time_days is not None else f.delivery_time_days
    else:
        f = SearchFilter(
            size_clothing=body.size_clothing,
            size_pants=body.size_pants,
            size_shoes=body.size_shoes,
            price_min=body.price_min,
            price_max=body.price_max,
            color=body.color,
            delivery_time_days=body.delivery_time_days,
        )
        db.add(f)
    db.commit()
    db.refresh(f)
    return FilterOut(**f.to_dict())

#commit
@app.get("/sessions/{session_id}/cart", response_model=CartSummaryOut)
def get_cart(session_id: str, db: Session = Depends(get_db)):
    """Kombinierten Warenkorb abrufen."""
    session = _get_session(session_id, db)
    return cart_to_summary(session)


@app.post("/sessions/{session_id}/cart/items")
def cart_add_item(
    session_id: str,
    body: AddToCartRequest,
    db: Session = Depends(get_db),
):
    """Produkt aus Suchergebnis in den Warenkorb legen."""
    session = _get_session(session_id, db)
    rp = RetailerProduct(
        retailer_id=body.retailer_id,
        product_id=body.product_id,
        title=body.title,
        price=body.price,
        currency=body.currency,
        delivery_estimate_days=body.delivery_estimate_days,
        image_url=body.image_url,
        product_url=body.product_url,
        variants=body.variants,
        raw={},
    )
    item = add_to_cart(db, session_id, rp, quantity=body.quantity)
    if not item:
        raise HTTPException(status_code=400, detail="Konnte nicht hinzugefügt werden")
    return {"cart_item_id": item.id, "message": "In den Warenkorb gelegt."}


@app.delete("/sessions/{session_id}/cart/items/{cart_item_id}")
def cart_remove_item(session_id: str, cart_item_id: int, db: Session = Depends(get_db)):
    """Item aus dem Warenkorb entfernen."""
    ok = remove_from_cart(db, session_id, cart_item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cart-Item nicht gefunden")
    return {"message": "Entfernt."}


@app.patch("/sessions/{session_id}/cart/items/{cart_item_id}")
def cart_update_quantity(
    session_id: str,
    cart_item_id: int,
    body: UpdateQuantityRequest,
    db: Session = Depends(get_db),
):
    """Menge eines Cart-Items ändern."""
    ok = update_cart_item_quantity(db, session_id, cart_item_id, body.quantity)
    if not ok:
        raise HTTPException(status_code=404, detail="Cart-Item nicht gefunden")
    return {"message": "Aktualisiert."}


@app.post("/sessions/{session_id}/checkout-simulation", response_model=CheckoutSimulationOut)
def checkout_simulation(session_id: str, db: Session = Depends(get_db)):
    """Simulierten Checkout ausführen (eine Adresse/Zahlung, Schritte pro Händler)."""
    session = _get_session(session_id, db)
    if not session.cart_items:
        raise HTTPException(status_code=400, detail="Warenkorb ist leer.")
    result = run_checkout_simulation(session)
    session.status = "checkout_simulated"
    db.commit()
    return result


@app.get("/api-test", include_in_schema=False)
def api_test_page():
    """Einfache HTML-Testseite für die API."""
    path = Path(__file__).parent / "api_test.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="api_test.html nicht gefunden")
    return FileResponse(path, media_type="text/html")


# Demo-Kategorien (keine externe API)
DEMO_CATEGORIES = [
    {"name": "Herren", "category_id": 1},
    {"name": "Damen", "category_id": 2},
    {"name": "Ski & Winter", "category_id": 3},
    {"name": "Party & Events", "category_id": 4},
    {"name": "Sport & Outdoor", "category_id": 5},
    {"name": "Streetwear", "category_id": 6},
]


@app.get("/categories", response_model=list[dict])
def list_categories():
    """Demo-Kategorien (name, category_id) – keine externe API."""
    return DEMO_CATEGORIES


@app.post("/categories/sync", response_model=dict)
def sync_categories():
    """Nur Demo-Daten: Kein Sync mit externer API."""
    return {"ok": True, "saved_count": 0, "message": "Nur Demo-Daten, kein Sync."}
