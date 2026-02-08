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

- **Kritisch für Suche.** Im Playground unter „Product Search and Listing“ / „Product“ die **exakte Request-URL** prüfen (nur der Pfad ab Host, z. B. `/api/v1/getProducts`).
- **Konfiguration:** In `.env` kannst du den exakten Pfad setzen: `ASOS_SEARCH_ENDPOINT=/api/v1/getProducts` (Wert aus dem Playground). Dann wird nur dieser Endpoint verwendet.
- **Ohne ASOS_SEARCH_ENDPOINT** probiert der Code nacheinander: `getProducts`, `getProductList`, `searchProducts`, `productSearch`, `products`, `product/list`, `search`, `product/search`, `v2/products/list`.
- **Parameter:** Es werden u. a. `query`/`q`/`keyword`/`searchTerm`, `limit`/`pageSize`, `country`/`store` ausprobiert.
- **Response:** Parser unterstützt `products`, `results`, `items`, `data`, `list`, `productList`. Felder: id/productId, price/priceInfo/currentPrice, name/title/productTitle, imageUrl, url/link, variants/sizes, delivery.

---

## 6. Product Detail (getProductDetails)

- **Methode:** GET
- **URL:** `https://asos10.p.rapidapi.com/api/v1/getProductDetails`
- **Parameter (laut Playground):**
  - `currency` (z. B. USD, EUR)
  - `store` (z. B. US, DE, GB)
  - `language` (z. B. en-US, de-DE)
  - `sizeSchema` (z. B. US, EU)
  - Für ein einzelnes Produkt zusätzlich: `productId` oder `id` oder `articleId`
- **Beispiel (cURL):**
  ```bash
  curl --request GET \
    --url 'https://asos10.p.rapidapi.com/api/v1/getProductDetails?currency=USD&store=US&language=en-US&sizeSchema=US' \
    --header 'x-rapidapi-host: asos10.p.rapidapi.com' \
    --header 'x-rapidapi-key: YOUR_KEY'
  ```
- Im Code: `get_product_detail(product_id, currency=..., store=..., language=..., country_code=...)` nutzt diesen Endpoint; für die Suche wird getProductDetails ebenfalls mit `currency`, `store`, `language`, `sizeSchema` (und ggf. `query`/`q`) probiert.

---

## Mapping KI-Brief → API

| Brief-Feld        | API-Nutzung |
|-------------------|-------------|
| country           | Land-Parameter (evtl. mit Get Countries validieren) |
| category          | Über Get Categories auf categoryId mappen |
| reason, preferences, must_haves | Zu Suchbegriff kombinieren |
| budget_currency   | Falls API Währung unterstützt |
| budget_min/max    | Nur wenn API Preis-Filter hat; sonst Ranking |
