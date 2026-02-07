from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import ShoppingSession, ShoppingRequirement, ConversationMessage
from schemas import (
    MessageRequest,
    MessageResponse,
    RequirementsOut,
    SessionResponse,
    MessageOut,
)
from agent import process_message
from asos_api import search_products_by_category

# ---------------------------------------------------------------------------
# Tabellen erstellen
# ---------------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Hacknation API",
    description="KI-Chat: Fragen stellen und Anforderungen speichern",
    version="0.1.0",
)

# CORS (Flutter Web: Port anpassen, z. B. 8080, 5354)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5354",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5354",
        "http://0.0.0.0:5173",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def _requirements_out(req: ShoppingRequirement | None) -> RequirementsOut:
    if req is None:
        return RequirementsOut()
    return RequirementsOut(**req.to_dict())


def _get_session_or_404(session_id: str, db: Session) -> ShoppingSession:
    session = db.query(ShoppingSession).filter(ShoppingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    return session


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Hacknation API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


# -- Sessions ---------------------------------------------------------------

@app.post("/sessions", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    """Erstellt eine neue Shopping-Session (nur Chat + Anforderungen)."""
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
        created_at=session.created_at,
    )


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Gibt eine Session mit Nachrichten und Anforderungen zurück."""
    session = _get_session_or_404(session_id, db)

    return SessionResponse(
        session_id=session.id,
        status=session.status,
        requirements=_requirements_out(session.requirements),
        messages=[
            MessageOut(role=m.role, content=m.content, created_at=m.created_at)
            for m in session.messages
        ],
        created_at=session.created_at,
    )


# -- Chat -------------------------------------------------------------------

@app.post("/sessions/{session_id}/chat", response_model=MessageResponse)
def chat(session_id: str, body: MessageRequest, db: Session = Depends(get_db)):
    """Sendet eine Nutzernachricht, KI antwortet und speichert Anforderungen."""
    session = _get_session_or_404(session_id, db)

    if session.status == "ready_for_search":
        raise HTTPException(
            status_code=400,
            detail="Anforderungen sind bereits vollständig.",
        )

    user_msg = ConversationMessage(
        session_id=session.id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    conversation = [
        {"role": m.role, "content": m.content} for m in session.messages
    ]
    current_reqs = session.requirements.to_dict() if session.requirements else None

    assistant_text, tool_calls = process_message(conversation, current_reqs)

    req = session.requirements
    for tc in tool_calls:
        if tc["name"] == "update_shopping_requirements":
            req.merge_update(tc["arguments"])
        elif tc["name"] == "mark_requirements_complete":
            req.is_complete = True
            session.status = "ready_for_search"

    if req:
        db.add(req)
        db.add(session)

    assistant_msg = ConversationMessage(
        session_id=session.id,
        role="assistant",
        content=assistant_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(session)
    db.refresh(req)

    # Wenn die KI gerade abgeschlossen hat: automatisch ASOS-Suche mit von der KI gespeicherter Kategorie (Limit 10)
    products: list[dict] = []
    if session.status == "ready_for_search" and req:
        currency = (req.budget_currency or "USD").upper()
        country = _country_to_code(req.country) if req.country else "US"
        result = search_products_by_category(
            req.category,
            currency=currency,
            country=country,
            store=country,
            limit=10,
            offset=0,
        )
        products = result.get("products", []) or []

    return MessageResponse(
        session_id=session.id,
        reply=assistant_text,
        requirements=_requirements_out(session.requirements),
        status=session.status,
        products=products,
    )


# -- Suche (ASOS) ------------------------------------------------------------

@app.get("/sessions/{session_id}/search/products")
def search_session_products(
    session_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Sucht bei ASOS (RapidAPI) nach Produkten zur Kategorie der Session.
    Nutzt exakt die in der KI gespeicherte category (clothing, food, both, other).
    Standard-Limit: 10 Produkte.
    """
    session = _get_session_or_404(session_id, db)
    req = session.requirements
    if not req:
        raise HTTPException(
            status_code=400,
            detail="Keine Anforderungen für diese Session.",
        )

    # Suchbegriff kommt ausschließlich aus der von der KI gespeicherten Kategorie (clothing, food, both, other)
    currency = (req.budget_currency or "USD").upper()
    country = _country_to_code(req.country) if req.country else "US"
    store = country

    result = search_products_by_category(
        req.category,
        currency=currency,
        country=country,
        store=store,
        limit=limit,
        offset=offset,
    )

    if "error" in result and result.get("products") == []:
        raise HTTPException(
            status_code=502,
            detail=result.get("error", "ASOS-Suche fehlgeschlagen"),
        )

    return {
        "session_id": session_id,
        "search_term": search_term,
        "category": req.category,
        "products": result.get("products", []),
        "count": result.get("count", 0),
    }


def _country_to_code(country: str) -> str:
    """Land-Name oder -Code auf 2-Buchstaben-Code für ASOS mappen."""
    m = {
        "germany": "DE",
        "deutschland": "DE",
        "us": "US",
        "usa": "US",
        "united states": "US",
        "uk": "GB",
        "united kingdom": "GB",
        "gb": "GB",
        "france": "FR",
        "italy": "IT",
        "spain": "ES",
        "austria": "AT",
        "switzerland": "CH",
    }
    key = (country or "").strip().lower()
    return m.get(key, "US")
