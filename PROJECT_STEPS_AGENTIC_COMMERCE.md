# Agentic Commerce — Projekt in sinnvolle Schritte unterteilt

VC-Track-Ziel: **Conversational, agentic shopping** — Nutzer beschreiben, was sie wollen; ein AI-Agent übernimmt das Finden und (simulierte) Kaufen über mehrere Händler.

---

## Szenario wählen (Scope für 24h)

**Empfehlung:** **Option B: Skiing Outfit**  
- Klar abgegrenzt (ein Outfit, Größe, Budget, Lieferfrist)  
- Gut zu eurem bestehenden Modell (category: clothing, reason: ski)  
- Weniger Komplexität als Hackathon Host Kit (60 Personen, viele Kategorien)

Alternativ: **Option A (Super Bowl Outfit)** oder **Option C (Hackathon Host Kit)** — dann Anforderungen und Suchlogik entsprechend anpassen.

---

## Ist-Zustand (bereits im Projekt)

| VC-Anforderung | Status | Wo im Projekt |
|----------------|--------|----------------|
| **2.1 Conversational Brief & Constraints** | ✅ Vorhanden | `agent.py` (ShopBuddy), `update_shopping_requirements` / `mark_requirements_complete`, `ShoppingRequirement` (Budget, Lieferfrist, Präferenzen, Must-/Nice-to-haves) |
| **Structured Shopping Spec (JSON)** | ✅ Vorhanden | `ShoppingRequirement.to_dict()` → RequirementsOut (Pydantic) |
| **Multi-Retailer Discovery (≥3)** | ❌ Fehlt | Kein produktiver Multi-Retailer-Suchlayer; ggf. alte ASOS-Integration entfernt |
| **Ranking Engine** | ❌ Fehlt | Kein transparentes Scoring |
| **Combined Cart View** | ❌ Fehlt | Kein Warenkorb-Modell, keine Cart-API |
| **Checkout (simuliert)** | ❌ Fehlt | Kein Checkout-Flow |

---

## Phasen und konkrete Schritte

### Phase 1: Brief & Spec abschließen (≈ 1–2 h)

Ziel: Sicherstellen, dass der Agent alle VC-relevanten Felder erfasst und ein **Shopping Spec (JSON)** ausgibt.

- [ ] **1.1** Szenario-spezifische Felder im Agent prüfen/ergänzen  
  - Für Skiing: `size` (z. B. M), `style` (warm, waterproof), `category=clothing`, `reason`/`event_type=ski`.  
  - System-Prompt in `agent.py` ggf. um „Größe“, „wasserdicht“, „warm“ erweitern.
- [ ] **1.2** Spec-Output definieren  
  - Ein klares JSON-Schema für „Shopping Spec“ (z. B. als Pydantic-Modell in `schemas.py`) das aus `ShoppingRequirement` abgeleitet wird.  
  - Optional: Endpoint `GET /sessions/{id}/spec` der das strukturierte Spec zurückgibt (für Frontend & Such-Service).

**Ergebnis:** Strukturierter Shopping-Spec (JSON) pro Session, der als Input für Phase 2 dient.

---

### Phase 2: Multi-Retailer Discovery (≥ 3 Händler) (≈ 4–6 h)

Ziel: Produkte von **mindestens 3** verschiedenen Quellen holen; pro Item: Preis, Liefer-Schätzung, Varianten, Händler-Identität.

- [ ] **2.1** Einheitliches **Produktmodell** definieren  
  - In `schemas.py` (oder `models.py`): z. B. `ProductItem` mit `id`, `name`, `price`, `currency`, `delivery_estimate`, `retailer_id`, `retailer_name`, `url`, `image_url`, `variants` (optional).  
  - So können alle Händler-Adapter dasselbe Format liefern.
- [ ] **2.2** Drei Händler-Quellen anbinden  
  - **Option A (Real):** 3 echte APIs (z. B. ASOS, ein weiterer Fashion-API, ein dritter) — je nach Verfügbarkeit und Keys.  
  - **Option B (Demo):** 2–3 **gemockte** Retailer-APIs mit realistischen Daten (z. B. `mock_retailer_a.py`, `mock_retailer_b.py`, `mock_retailer_c.py`), die dasselbe `ProductItem`-Format zurückgeben.  
  - Gemeinsamer **Discovery-Service** (z. B. `services/discovery.py`): nimmt Shopping-Spec, ruft alle 3 Quellen parallel auf, aggregiert Ergebnisse.
- [ ] **2.3** Such-API anbinden  
  - `POST /sessions/{session_id}/search` (oder `GET .../search/products`)  
  - Input: session_id (Spec aus DB lesen).  
  - Output: Liste von `ProductItem` von allen Händlern (noch unranked).  
  - Session-Status auf `searching` → nach Abschluss `done` oder nächster Status.

**Ergebnis:** Ein Aufruf liefert Produkte von ≥3 Händlern mit Preis, Lieferung, Händler, Varianten.

---

### Phase 3: Ranking Engine (transparent) (≈ 2–3 h)

Ziel: **Nicht nur LLM-Output** — Ranking nach nachvollziehbarer Logik; Agent kann begründen: „Warum ist Option #1?“

- [ ] **3.1** Scoring-Kriterien festlegen  
  - z. B. Punkte für: Gesamtkosten (im Budget), Lieferfrist (vor Deadline), Präferenz-Match (Stil/Größe), Set-Kohärenz (z. B. „komplettes Ski-Outfit“).  
  - Gewichte definieren (z. B. 40 % Preis, 30 % Lieferung, 30 % Präferenz).
- [ ] **3.2** Ranking-Modul implementieren  
  - Funktion `rank_products(spec, products) -> list[RankedProduct]`  
  - Jedes `RankedProduct`: Produkt + `score`, `score_breakdown` (z. B. `{"cost": 0.8, "delivery": 1.0, "preference": 0.6}`).  
  - Sortierung nach Gesamt-Score.
- [ ] **3.3** „Warum #1?“-Erklärung  
  - Entweder im Backend: kurze Begründung aus `score_breakdown` generieren (template oder kleines LLM-Call).  
  - Oder Struktur `ranking_explanation` an Frontend liefern; Frontend zeigt Breakdown (z. B. „Günstig, lieferbar bis X, passt zu deinen Präferenzen“).
- [ ] **3.4** Suche mit Ranking verknüpfen  
  - Nach Discovery: `rank_products(session.requirements, products)` aufrufen und sortierte Liste (+ Erklärung) zurückgeben.

**Ergebnis:** Transparentes Ranking mit Begründung; keine reine LLM-Sortierung.

---

### Phase 4: Combined Cart (≈ 3–4 h)

Ziel: **Ein** Warenkorb über alle Händler; Gesamtkosten, Lieferung pro Position; Nutzer kann ersetzen/optimieren.

- [ ] **4.1** Cart-Datenmodell  
  - Neue Tabelle `cart_items` (oder Äquivalent): `session_id`, `product_id`, `retailer_id`, `quantity`, `price`, `delivery_estimate`, `added_at`.  
  - Relation: Session → Cart Items (oder eigenes Cart-Objekt pro Session).
- [ ] **4.2** Cart-API  
  - `GET /sessions/{session_id}/cart` → kombinierter Warenkorb (alle Händler), Gesamtpreis, pro Item Lieferung.  
  - `POST /sessions/{session_id}/cart/items` → Item hinzufügen (aus Suchergebnissen).  
  - `DELETE /sessions/{session_id}/cart/items/{item_id}` oder `PUT .../items/{item_id}` (Menge/Ersetzen).  
  - Optional: `POST .../cart/optimize` → Agent schlägt Ersetzungen vor (Stretch).
- [ ] **4.3** Combined Cart View (UI)  
  - Im Frontend: eine Liste mit allen Cart-Items, gruppiert nach Händler oder flach mit Händler-Label; Summe, Lieferdatum pro Zeile.  
  - Buttons: Entfernen, Ersetzen (zurück zur Suche/Alternativen).
- [ ] **4.4** Agent-Anpassung: Cart-Modifikation  
  - Wenn Nutzer „ersetze Jacke“ oder „nimm was Günstigeres“ sagt: Tool/Flow, der Cart-Items tauscht oder neue Suchanfrage auslöst und Cart aktualisiert.  
  - Damit erfüllt: „User can modify the cart and the agent adapts“.

**Ergebnis:** Ein kombinierter Warenkorb über ≥3 Händler, änderbar durch Nutzer/Agent.

---

### Phase 5: Checkout (simuliert / Sandbox) (≈ 2–3 h)

Ziel: **Kein echtes Geld** — nur Demo: eine Adresse/Zahlung einmal eingeben, Agent „fächert“ Checkout pro Händler auf (simuliert).

- [ ] **5.1** Checkout-Daten  
  - Adresse + Zahlungsmethode (Mock) einmal pro Session speichern (z. B. `checkout_profile` oder in Session).  
  - Keine echten Payment-Daten; nur Platzhalter oder Sandbox-Felder.
- [ ] **5.2** Checkout-Orchestrierung  
  - `POST /sessions/{session_id}/checkout/start`  
  - Input: Adresse, „Zahlung“ (Mock).  
  - Backend: für jeden Händler im Cart einen **simulierten** Checkout-Schritt (z. B. „Step 1: Retailer A – Form prefilled“, „Step 2: Retailer B – Form prefilled“).  
  - Response: Liste von „Checkout-Steps“ (retailer, url oder deep link, autofill-Preview als Text/JSON).  
  - Optional: einfache Replay-Seite (z. B. in `api_test.html` oder Flutter): Buttons „Step 1 ausführen“, „Step 2 ausführen“ mit Anzeige der vorausgefüllten Daten.
- [ ] **5.3** Dokumentation  
  - In API-Docs klar machen: Checkout ist nur Simulation/Sandbox; keine echten Transaktionen.

**Ergebnis:** Einmal Adresse/Zahlung eingeben → Agent zeigt aufgeteilte Checkout-Schritte pro Händler (simuliert).

---

### Phase 6: Integration & Demo-Flow (≈ 2 h)

- [ ] **6.1** End-to-End-Flow  
  - Session erstellen → Chat bis `ready_for_search` → Automatisch oder explizit Suche starten → Ranking → Combined Cart anzeigen → Nutzer kann anpassen → Checkout (simuliert) starten.
- [ ] **6.2** Flutter/Frontend  
  - Chat, dann Produktliste (ranked), dann Cart-View, dann Checkout-Buttons; ggf. `API_FOR_FLUTTER.md` aktualisieren.
- [ ] **6.3** Kurze Pitchesätze  
  - „Warum #1?“ (Ranking), „Ein Warenkorb, drei Händler“, „Checkout einmal eingeben, Agent verteilt auf Händler“.

---

## Optional (Stretch)

- Budget-Optimierer („gleiches Setup, günstiger“)  
- Liefer-Optimierer („alles bis Freitag“)  
- Stil-/Kategorie-Kohärenz im Scoring  
- Return-aware Ranking  
- Explain-Mode (Decision-Trace des Agents)

---

## Kurz-Checkliste VC-Constraints

- [ ] Kein einfacher Recommendation-Chatbot (Agent zerlegt Intent, sucht, rankt, Cart, Checkout).  
- [ ] Kein Single-Retailer (≥3 Händler).  
- [ ] Combined Cart UI vorhanden.  
- [ ] Checkout nur simuliert/sandboxed.  
- [ ] Nutzer kann Cart anpassen, Agent reagiert darauf.

---

## Zeiten (Orientierung 24h)

| Phase | Grob |
|-------|------|
| 1 – Brief & Spec | 1–2 h |
| 2 – Multi-Retailer Discovery | 4–6 h |
| 3 – Ranking | 2–3 h |
| 4 – Combined Cart | 3–4 h |
| 5 – Checkout (simuliert) | 2–3 h |
| 6 – Integration & Demo | 2 h |

Wenn ihr zuerst mit **gemockten** Händlern arbeitet (Phase 2 Option B), spart ihr Zeit für API-Keys und könnt Cart, Ranking und Checkout stabil durchspielen.

Viel Erfolg beim Hackathon.
