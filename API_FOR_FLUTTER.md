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
| POST | `/sessions/{session_id}/chat` | Eine Nachricht senden, Antwort als JSON (inkl. ggf. Produkte) |
| GET | `/sessions/{session_id}/search/products` | Produkte zur Session-Kategorie suchen (ASOS, optional limit/offset) |

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
  "status": "gathering_info",
  "products": []
}
```

- **Status:**  
  - `gathering_info` = KI sammelt noch Infos  
  - `ready_for_search` = KI hat abgeschlossen → **Suche startet automatisch**

- **Automatische Produktsuche:** Sobald die KI alle Infos hat und `status === "ready_for_search"` ist, führt die API **automatisch** eine ASOS-Suche aus (Suchbegriff = gespeicherte **category**: `clothing`, `food`, `both`, `other`). Die Antwort enthält dann bis zu **10 Produkte** im Feld `products`. Du musst also **keinen** separaten Aufruf starten – die Produkte kommen direkt in der Chat-Response.

- Wenn `status === "ready_for_search"`, antwortet die API mit 400, falls man erneut `/chat` aufruft.

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

## 5. Produkte anzeigen (Flutter)

Die Produkte kommen entweder **automatisch** in der Chat-Response (`POST .../chat`), sobald `status === "ready_for_search"` ist, oder du holst sie nach mit **GET** `/sessions/{session_id}/search/products` (z. B. `?limit=10&offset=0`).

### Automatisch Produkte laden, wenn das Gespräch endet

Sobald die KI mit „Ich habe alle Angaben gespeichert“ o. ä. antwortet, ist `status === "ready_for_search"`. Die **Produkte liegen dann schon in derselben Chat-Response** – du brauchst **keinen** zweiten Request, wenn du die Response auswertest.

**Ablauf in Flutter:**

1. Nach **jeder** Chat-Nachricht (POST `/sessions/{session_id}/chat`) die Response parsen.
2. **Wenn** `response.status == "ready_for_search"`:
   - **Option A (empfohlen):** `response.products` direkt verwenden und in der UI anzeigen (z. B. Liste unter dem Chat oder eigene Produkt-Seite).
   - **Option B (Fallback):** Wenn `response.products` leer ist (z. B. weil die ASOS-API kurz nicht erreichbar war), **dann** einmalig **GET** `/sessions/{session_id}/search/products` aufrufen und die zurückgegebenen Produkte anzeigen.

**Beispiel: Nach dem Senden einer Chat-Nachricht**

```dart
Future<void> sendMessage(String text) async {
  final response = await http.post(
    Uri.parse('$baseUrl/sessions/$sessionId/chat'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'message': text}),
  );

  if (response.statusCode != 200) {
    // Fehler anzeigen (z. B. response.body oder detail)
    return;
  }

  final data = jsonDecode(response.body);
  final status = data['status'] as String?;
  final reply = data['reply'] as String? ?? '';

  // Nachricht wie gewohnt anzeigen
  addAssistantMessage(reply);

  // Sobald die KI fertig ist: Produkte aus der Response nutzen oder nachladen
  if (status == 'ready_for_search') {
    List<dynamic> products = data['products'] as List<dynamic>? ?? [];
    if (products.isNotEmpty) {
      setState(() {
        productList = products.map((e) => ProductItem.fromJson(e as Map<String, dynamic>)).toList();
      });
      // Optional: zur Produktansicht wechseln oder Sektion unter dem Chat einblenden
      // Navigator.push(...) oder _showProductSection = true;
    } else {
      // Fallback: Produkte separat abrufen
      await fetchProducts();
    }
  }
}

Future<void> fetchProducts() async {
  final response = await http.get(
    Uri.parse('$baseUrl/sessions/$sessionId/search/products?limit=10&offset=0'),
  );
  if (response.statusCode != 200) return;
  final data = jsonDecode(response.body);
  final list = data['products'] as List<dynamic>? ?? [];
  setState(() {
    productList = list.map((e) => ProductItem.fromJson(e as Map<String, dynamic>)).toList();
  });
}
```

Kurz: **Einmal** `POST .../chat` ausführen → in der Antwort `status` prüfen → bei `"ready_for_search"` die `products` aus der gleichen Response nehmen (oder bei leeren `products` einmal `GET .../search/products` aufrufen). So werden die Produkte automatisch angezeigt, sobald das Gespräch endet.

### Response-Struktur Produkte

`products` ist eine Liste von Objekten. Die ASOS-API kann je nach Endpunkt unterschiedliche Felder liefern; typisch sind z. B.:

- `name` / `productName` / `title` – Produktname  
- `price` / `price.current.value` – Preis  
- `imageUrl` / `imageUrl` / `media.images[0].url` – Bild-URL  
- `id` – Produkt-ID  
- `url` – Link zum Produkt  

Da die genaue Struktur variieren kann, in Flutter am besten ein flexibles Modell nutzen (z. B. `Map<String, dynamic>` oder ein Modell mit optionalen Feldern).

### Flutter: Produktliste anzeigen

Nach dem Chat-Aufruf: wenn `response.status == "ready_for_search"` und `response.products != null` und `response.products!.isNotEmpty`, die Liste anzeigen.

**1. Modell (Beispiel mit optionalen Feldern):**

```dart
class ProductItem {
  final String? id;
  final String? name;
  final String? imageUrl;
  final String? price;
  final String? url;

  ProductItem({
    this.id,
    this.name,
    this.imageUrl,
    this.price,
    this.url,
  });

  factory ProductItem.fromJson(Map<String, dynamic> json) {
    // ASOS / API-Struktur anpassen; oft verschachtelt (z. B. price.current.value)
    final priceObj = json['price'];
    final priceVal = priceObj is Map
        ? (priceObj['current']?['value'] ?? priceObj['value'] ?? priceObj)
        : priceObj;
    return ProductItem(
      id: json['id']?.toString(),
      name: json['name'] ?? json['productName'] ?? json['title'],
      imageUrl: json['imageUrl'] ?? json['media']?['images']?[0]?['url'],
      price: priceVal?.toString(),
      url: json['url'],
    );
  }
}
```

**2. Chat-Response erweitern:**

```dart
class MessageResponse {
  final String sessionId;
  final String reply;
  final RequirementsOut requirements;
  final String status;
  final List<ProductItem> products;

  MessageResponse({
    required this.sessionId,
    required this.reply,
    required this.requirements,
    required this.status,
    this.products = const [],
  });

  factory MessageResponse.fromJson(Map<String, dynamic> json) {
    final productsList = json['products'] as List<dynamic>? ?? [];
    return MessageResponse(
      sessionId: json['session_id'],
      reply: json['reply'],
      requirements: RequirementsOut.fromJson(json['requirements']),
      status: json['status'],
      products: productsList
          .map((e) => ProductItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
```

**3. UI: Liste der Produkte (z. B. unter dem Chat):**

```dart
if (messageResponse.status == 'ready_for_search' &&
    messageResponse.products.isNotEmpty) {
  Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text('Deine Produkte (${messageResponse.products.length})',
          style: Theme.of(context).textTheme.titleMedium),
      const SizedBox(height: 8),
      SizedBox(
        height: 220,
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          itemCount: messageResponse.products.length,
          itemBuilder: (context, index) {
            final p = messageResponse.products[index];
            return Card(
              margin: const EdgeInsets.only(right: 12),
              child: SizedBox(
                width: 160,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (p.imageUrl != null && p.imageUrl!.isNotEmpty)
                      Image.network(
                        p.imageUrl!,
                        height: 120,
                        width: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            const Icon(Icons.image_not_supported, size: 48),
                      ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            p.name ?? 'Produkt',
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 12),
                          ),
                          if (p.price != null)
                            Text(
                              '${p.price} €',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    ],
  )
}
```

So zeigst du die 10 Produkte direkt an, sobald die KI fertig ist – ohne weiteren API-Call. Wenn du später mehr laden willst, rufe `GET /sessions/{session_id}/search/products?limit=10&offset=10` auf.

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

5. **Produkte automatisch anzeigen, wenn das Gespräch endet**  
   Nach jedem `POST .../chat`: Wenn die Response `status === "ready_for_search"` hat, kommen die Produkte **in derselben Response** unter `products`. Einfach diese Liste in den State übernehmen und anzeigen (oder bei leeren `products` einmal `GET /sessions/{session_id}/search/products` aufrufen). Siehe Abschnitt 5 oben („Automatisch Produkte laden“) für den genauen Flutter-Code.

Damit kann dein Freund das Flutter-Frontend vollständig an die bestehende API anbinden.
