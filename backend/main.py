from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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


@app.get("/api-test", include_in_schema=False)
def api_test_page():
    """Einfaches HTML-Interface zum Testen der Routen (GET /api-test im Browser)."""
    path = Path(__file__).parent / "api_test.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="api_test.html nicht gefunden")
    return FileResponse(path, media_type="text/html")


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

    return MessageResponse(
        session_id=session.id,
        reply=assistant_text,
        requirements=_requirements_out(session.requirements),
        status=session.status,
    )
