"""
Agentic Commerce API – FastAPI Backend.
Konversationeller Brief, Multi-Händler-Suche, Ranking, kombinierter Warenkorb, simulierter Checkout.
"""
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import ShoppingSession, ShoppingRequirement, ConversationMessage, CartItem
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
    AddToCartRequest,
    UpdateQuantityRequest,
)
from agent import process_message
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


@app.post("/sessions", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    """Neue Shopping-Session anlegen (Brief + Cart)."""
    session = ShoppingSession()
    req = ShoppingRequirement(session_id=session.id)
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


def _product_summary(p: dict) -> dict:
    """Kurze Produkt-Info aus API-Dict (verschiedene Key-Namen)."""
    price = p.get("price")
    if price is None and isinstance(p.get("priceInfo"), dict):
        price = p.get("priceInfo", {}).get("current") or p.get("priceInfo", {}).get("value")
    return {
        "id": p.get("id") or p.get("productId") or p.get("articleId"),
        "name": (p.get("name") or p.get("title") or p.get("productTitle") or p.get("displayName") or "").strip() or None,
        "price": price,
    }


@app.get("/test-api", include_in_schema=False)
def test_api_requests(raw: bool = False, reload: bool = False):
    """
    Testet die ASOS-API: Referenzdaten (Categories, Countries, ReturnCharges) und getProductList.
    ?raw=1: zeigt die Response-Struktur von getProductList (Keys).
    ?reload=1: leert Caches und lädt Kategorien/Referenzdaten neu (mehr Kategorien bei verschachtelter API).
    """
    from api_service import clear_reference_data_cache, get_reference_data

    from retailers.asos_api import clear_reference_caches, get_product_list_raw

    if reload:
        clear_reference_caches()
        clear_reference_data_cache()

    result: dict = {"ok": True, "ref": {}, "product_list": {"count": 0, "sample": []}}
    try:
        ref = get_reference_data()
        cats = ref.get("categories") or []
        result["ref"] = {
            "categories_count": len(cats),
            "countries_count": len(ref.get("countries") or []),
            "return_charges": "present" if ref.get("return_charges") is not None else "missing",
        }
        if cats and len(cats) <= 5:
            result["ref"]["category_sample_keys"] = [list(c.keys()) for c in cats[:2]]
    except Exception as e:
        result["ok"] = False
        result["ref_error"] = str(e)
        return result

    try:
        products, raw_response = get_product_list_raw(
            category_id=None,
            currency="USD",
            country="US",
            store="US",
            language_short="en",
            size_schema="US",
            limit=10,
            offset=0,
            sort="recommended",
        )
        result["product_list"]["count"] = len(products)
        result["product_list"]["sample"] = [_product_summary(p) for p in (products[:5] if products else [])]
        if raw and raw_response is not None:
            if isinstance(raw_response, dict):
                result["product_list"]["_debug_response_keys"] = list(raw_response.keys())
                result["product_list"]["_debug_value_types"] = {
                    k: type(v).__name__ + (" (len=%s)" % len(v) if isinstance(v, (list, dict)) else "")
                    for k, v in raw_response.items()
                }
                # Bei status+message: Inhalt von message anzeigen (oft Fehlermeldung der API)
                if set(raw_response.keys()) <= {"status", "message"}:
                    msg = raw_response.get("message")
                    if isinstance(msg, list):
                        result["product_list"]["_debug_message_content"] = msg[:5]
                    else:
                        result["product_list"]["_debug_message_content"] = msg
            else:
                result["product_list"]["_debug_response_type"] = type(raw_response).__name__
    except Exception as e:
        result["ok"] = False
        result["product_list_error"] = str(e)
    return result
