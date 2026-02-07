# Hacknation

Projekt mit Backend (FastAPI) und Frontend.

## Struktur

- **backend/** – FastAPI-Server
- **frontend/** – Frontend-Anwendung

## Schnellstart

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

→ API: http://127.0.0.1:8000 | Docs: http://127.0.0.1:8000/docs

### Frontend

Siehe `frontend/README.md` für ein Framework-Setup (z. B. Vite + React) oder öffne `frontend/index.html` in einem lokalen Server.
