# Backend (FastAPI)

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Starten

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Damit ist die API von überall erreichbar (z. B. für Frontend auf 0.0.0.0):

- API: http://0.0.0.0:8000 (bzw. http://127.0.0.1:8000 lokal)
- Dokumentation: http://0.0.0.0:8000/docs
