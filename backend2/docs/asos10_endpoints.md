# ASOS10 RapidAPI – Endpoints (DataCrawler)

API: [ASOS asos10](https://rapidapi.com/DataCrawler/api/asos10) auf RapidAPI.  
Basis-URL: `https://asos10.p.rapidapi.com`  
Header: `X-RapidAPI-Key`, `X-RapidAPI-Host: asos10.p.rapidapi.com`

---

## 1. Get Countries

- **Methode:** GET
- **URL:** `https://asos10.p.rapidapi.com/api/v1/getCountries`
- **Parameter:** Keine (laut Playground „No additional params“).
- **Response:** Im Playground prüfen und hier ergänzen (z. B. Liste von `{ "code": "DE", "name": "Germany" }` o. ä.). Wird für Validierung/Mapping von `spec.country` genutzt.

---

## 2. Get Categories

- **Methode:** GET
- **URL:** `https://asos10.p.rapidapi.com/api/v1/getCategories`
- **Parameter:** Keine.
- **Response:** Im Playground prüfen (z. B. Array von Kategorien mit `id`, `name`). Mapping: `category` (clothing/food/both/other) → konkrete Kategorie-IDs für die Produktsuche.

---

## 3. Get Return Charges

- **Methode:** GET
- **URL:** `https://asos10.p.rapidapi.com/api/v1/getReturnCharges` (oder vom Playground übernehmen)
- **Parameter:** Ggf. vom Playground (z. B. Land).
- **Response:** Optional für Checkout-Simulation; Format aus Playground übernehmen.

---

## 4. Test

- **Methode:** GET
- **URL:** vom Playground (z. B. `/api/v1/test`)
- Optional; für API-Checks.

---

## 5. Product Search / Listing

- **Kritisch für Suche.** Exakte URL und Parameter im Playground unter „Product Search and Listing“ bzw. „Product“ prüfen.
- **Vermutung (ohne Playground):** GET `https://asos10.p.rapidapi.com/api/v1/searchProducts` oder `/api/v1/products` mit Query-Parametern z. B.:
  - `query` / `q` / `keyword`: Suchbegriff (aus KI-Brief: reason, event_type, preferences, must_haves)
  - `country` / `store`: Land (aus spec.country)
  - `categoryId` / `category`: aus Get-Categories-Mapping
  - `limit` / `pageSize`: Anzahl
- **Response:** Typisch `products[]` oder `items[]` mit Objekten (id, title/name, price, imageUrl, url, variants, delivery). Parser in `asos_api._parse_asos_response` an die tatsächliche Struktur anpassen.

---

## 6. Product Detail (einzelnes Produkt)

- Falls im Playground ein Endpoint für ein einzelnes Produkt existiert (z. B. `/api/v1/product?id=...`): für Warenkorb-Details oder Checkout nutzen.
- URL/Parameter/Response aus Playground hier ergänzen.

---

## Mapping KI-Brief → API

| Brief-Feld        | API-Nutzung |
|-------------------|-------------|
| country           | Land-Parameter (evtl. mit Get Countries validieren) |
| category          | Über Get Categories auf categoryId mappen |
| reason, preferences, must_haves | Zu Suchbegriff kombinieren |
| budget_currency   | Falls API Währung unterstützt |
| budget_min/max    | Nur wenn API Preis-Filter hat; sonst Ranking |
