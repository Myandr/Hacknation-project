# Backend (FastAPI + AI Shopping Agent)

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Konfiguration

Kopiere `.env.example` nach `.env` und trage deinen OpenAI API Key ein:

```bash
cp .env.example .env
# Dann .env editieren und OPENAI_API_KEY setzen
```

## Starten

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://0.0.0.0:8000
- Swagger-Docs: http://0.0.0.0:8000/docs

## API-Endpunkte

| Methode | Pfad                          | Beschreibung                          |
| ------- | ----------------------------- | ------------------------------------- |
| GET     | `/`                           | API-Info                              |
| GET     | `/health`                     | Health-Check                          |
| POST    | `/sessions`                   | Neue Shopping-Session erstellen       |
| GET     | `/sessions/{id}`              | Session + Nachrichten + Requirements  |
| POST    | `/sessions/{id}/chat`         | Nachricht senden → AI-Antwort erhalten|

## Architektur

```
backend/
├── main.py          # FastAPI App + Routes
├── database.py      # SQLAlchemy Engine / Session
├── models.py        # DB-Modelle (ShoppingSession, Requirements, Messages)
├── schemas.py       # Pydantic Request/Response Schemas
├── agent.py         # AI Agent (OpenAI Function Calling)
├── requirements.txt
├── .env.example
└── README.md
```

## Testen

**Variante A – Swagger (im Browser)**  
1. Server starten: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Öffne http://127.0.0.1:8000/docs
3. `POST /sessions` ausführen → `session_id` aus der Response kopieren
4. `POST /sessions/{session_id}/chat` ausführen, Body z. B.: `{"message": "Ich brauche Outfits für eine Hochzeit, Budget 500€"}`  
   Der Agent antwortet und stellt Rückfragen.

**Variante B – Testseite (Chat-UI)**  
1. Server starten (wie oben)
2. `frontend/chat-test.html` im Browser öffnen (per Doppelklick oder `python -m http.server 8080` im Projektroot, dann http://localhost:8080/frontend/chat-test.html)
3. Eine Nachricht eingeben und Senden – die Antwort und die gespeicherten Anforderungen erscheinen unterhalb.

## Flow

1. Frontend erstellt eine Session (`POST /sessions`)
2. User schickt eine Nachricht (`POST /sessions/{id}/chat`)
3. AI analysiert die Nachricht und extrahiert:
   - Budget (min/max, Währung)
   - Lieferfrist
   - Präferenzen (Stil, Marken, Farben …)
   - Must-Haves & Nice-to-Haves
   - Anlass / Event-Infos (Personenanzahl, Grund)
4. AI fragt nach fehlenden Infos
5. Sobald alles komplett → Status wechselt zu `ready_for_search`
