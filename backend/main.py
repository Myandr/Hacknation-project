from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hacknation API",
    description="Backend API für das Hacknation-Projekt",
    version="0.1.0",
)

# CORS für Frontend-Zugriff (localhost + 0.0.0.0 für Netzwerk-Zugriff)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:5173",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hacknation API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
