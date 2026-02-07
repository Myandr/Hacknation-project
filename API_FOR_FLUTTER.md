# Hacknation API – Anbindung Flutter Frontend

Diese API steuert den KI-Chat: Session anlegen, Nachrichten senden, gespeicherte Anforderungen abrufen.

---

## Basis-URL

- **Lokal (Backend auf dem gleichen Rechner):** `http://127.0.0.1:8000`
- **Android-Emulator → Host:** `http://10.0.2.2:8000`
- **iOS-Simulator → localhost:** `http://127.0.0.1:8000`
- **Physisches Gerät / anderer Rechner:** `http://<IP-DES-BACKEND-RECHNERS>:8000` (z. B. `http://192.168.1.100:8000`)

Backend starten: im Ordner `backend` → `uvicorn main:app --reload --host 0.0.0.0` (damit Anfragen von anderen Geräten angenommen werden).

**CORS:** Flutter Web läuft im Browser – dafür sind in der API bereits u. a. `localhost:8080` und `localhost:5354` erlaubt. Anderer Port? In `backend/main.py` bei `allow_origins` eintragen.

---

## Übersicht Endpoints

| Methode | Pfad | Beschreibung |
|--------|------|----------------|
| GET | `/` | Kurzinfo + Link zu Docs |
| GET | `/health` | Health-Check |
| POST | `/sessions` | Neue Session erstellen |
| GET | `/sessions/{session_id}` | Session inkl. Nachrichten & Requirements laden |
| POST | `/sessions/{session_id}/chat` | Eine Nachricht senden, Antwort als JSON |

**Interaktive Docs:** Im Browser `http://127.0.0.1:8000/docs` öffnen (Swagger UI).

---

## 1. Session erstellen

**POST** `/sessions`

- **Request:** Kein Body nötig.
- **Response:** `200 OK`, JSON:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "gathering_info",
  "requirements": {
    "budget_min": null,
    "budget_max": null,
    "budget_currency": null,
    "delivery_deadline": null,
    "category": null,
    "country": null,
    "city": null,
    "event_type": null,
    "event_name": null,
    "people_count": null,
    "reason": null,
    "preferences": [],
    "must_haves": [],
    "nice_to_haves": [],
    "is_complete": false
  },
  "messages": [],
  "created_at": "2025-02-07T12:00:00.000Z"
}
```

**Flutter:** `session_id` speichern und für alle weiteren Requests verwenden.

---

## 2. Session abrufen (inkl. Verlauf)

**GET** `/sessions/{session_id}`

- **Response:** `200 OK`, gleiche Struktur wie bei „Session erstellen“, aber mit gefülltem `messages`-Array und aktuellen `requirements`.

**Beispiel `messages`:**

```json
"messages": [
  { "role": "user", "content": "Ich brauche was für eine Hochzeit", "created_at": "..." },
  { "role": "assistant", "content": "Cool! Wann und für wie viele Leute?", "created_at": "..." }
]
```

---

## 3. Chat (eine Nachricht, Antwort als JSON)

**POST** `/sessions/{session_id}/chat`

- **Request-Header:** `Content-Type: application/json`
- **Request-Body:**

```json
{
  "message": "Nächsten Samstag, 10 Leute, Budget 200€"
}
```

- **Response:** `200 OK`:

```json
{
  "session_id": "...",
  "reply": "Super, dann schauen wir mal...",
  "requirements": { ... },
  "status": "gathering_info"
}
```

- **Status:**  
  - `gathering_info` = KI sammelt noch Infos  
  - `ready_for_search` = KI hat abgeschlossen (`is_complete: true`)

Wenn `status === "ready_for_search"`, antwortet die API mit 400, falls man erneut `/chat` aufruft.

---

## 4. Datenmodell „Requirements“

Die KI füllt `requirements` schrittweise (Anlass, Budget, Wünsche usw.):

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| budget_min | number? | Min. Budget |
| budget_max | number? | Max. Budget |
| budget_currency | string? | z. B. "EUR" |
| delivery_deadline | string? | z. B. "2025-03-01" |
| category | string? | "clothing", "food", "both", "other" |
| country | string? | Land |
| city | string? | Stadt |
| event_type | string? | z. B. "Hochzeit" |
| event_name | string? | Name des Events |
| people_count | number? | Anzahl Personen |
| reason | string? | Grund/Anlass |
| preferences | string[] | Präferenzen |
| must_haves | string[] | Muss-Kriterien |
| nice_to_haves | string[] | Nice-to-have |
| is_complete | bool | true = KI hat abgeschlossen |

In Flutter kannst du dafür ein eigenes Modell (z. B. `ShoppingRequirements`) mit denselben Feldern anlegen und die JSON-Responses darauf mappen.

---

## Fehlerbehandlung

- **404** – Session nicht gefunden (z. B. falsche `session_id`). Body oft: `{"detail": "Session nicht gefunden"}`.
- **400** – Ungültiger Request oder Session bereits abgeschlossen (`status === "ready_for_search"`). Body: `{"detail": "..."}`.

Flutter: Statuscode prüfen und bei 4xx/5xx `detail` anzeigen oder in der App verarbeiten.

---

## Kurzablauf im Flutter-Frontend

1. **App-Start / „Neuer Chat“**  
   `POST /sessions` → `session_id` und erste `requirements` speichern.

2. **Nachrichten anzeigen**  
   Optional `GET /sessions/{session_id}` um Verlauf + aktuellen Stand zu laden.

3. **Nutzer schreibt Nachricht**  
   `POST /sessions/{session_id}/chat` mit `{"message": "..."}` → Antwort enthält `reply`, `requirements`, `status`. Diese in der UI anzeigen.

4. **Requirements anzeigen**  
   Aus `requirements` in Session- oder Chat-Response die gespeicherten Anforderungen (Budget, Anlass, etc.) in der UI anzeigen.

Damit kann dein Freund das Flutter-Frontend vollständig an die bestehende API anbinden.
