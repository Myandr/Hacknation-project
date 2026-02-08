"""
Statische „Essen-API“-Daten – nur im Quellcode, keine externe API.
Realistische Lebensmittel-Produkte für Suche bei category=food.
Format kompatibel mit SerpAPI shopping_results (title, link, price, thumbnail, source).
"""

# Real-life-artige Lebensmittel-Produkte (Demo-Daten im Code)
ESSEN_PRODUKTE = [
    # Snacks & Party
    {"title": "Pringles Original Chips 165g", "price": "2.49", "source": "Rewe", "link": "https://shop.rewe.de/pringles-original", "thumbnail": "", "product_id": "essen-rewe-1"},
    {"title": "Lorenz Crunchips Paprika 175g", "price": "1.99", "source": "Edeka", "link": "https://www.edeka.de/lorenz-crunchips", "thumbnail": "", "product_id": "essen-edeka-1"},
    {"title": "Haribo Goldbären 200g", "price": "1.79", "source": "Rewe", "link": "https://shop.rewe.de/haribo-goldbaeren", "thumbnail": "", "product_id": "essen-rewe-2"},
    {"title": "M&M's Erdnuss 180g", "price": "2.29", "source": "DM", "link": "https://www.dm.de/mms", "thumbnail": "", "product_id": "essen-dm-1"},
    {"title": "Studentenfutter 200g", "price": "3.49", "source": "Rewe", "link": "https://shop.rewe.de/studentenfutter", "thumbnail": "", "product_id": "essen-rewe-3"},
    {"title": "Oreo Original 154g", "price": "1.99", "source": "Edeka", "link": "https://www.edeka.de/oreo", "thumbnail": "", "product_id": "essen-edeka-2"},
    {"title": "Nutella 400g", "price": "4.49", "source": "Rewe", "link": "https://shop.rewe.de/nutella", "thumbnail": "", "product_id": "essen-rewe-4"},
    {"title": "Merci Edel-Nougat 300g", "price": "5.99", "source": "Rewe", "link": "https://shop.rewe.de/merci", "thumbnail": "", "product_id": "essen-rewe-5"},
    {"title": "Ritter Sport Marzipan 100g", "price": "1.69", "source": "Edeka", "link": "https://www.edeka.de/ritter-sport", "thumbnail": "", "product_id": "essen-edeka-3"},
    {"title": "Tuc Crackers Original 200g", "price": "1.49", "source": "Rewe", "link": "https://shop.rewe.de/tuc", "thumbnail": "", "product_id": "essen-rewe-6"},
    {"title": "Erdnussflips 150g", "price": "1.29", "source": "Lidl", "link": "https://www.lidl.de/erdnussflips", "thumbnail": "", "product_id": "essen-lidl-1"},
    {"title": "Salzstangen 200g", "price": "0.99", "source": "Aldi", "link": "https://www.aldi.de/salzstangen", "thumbnail": "", "product_id": "essen-aldi-1"},
    # Getränke
    {"title": "Coca-Cola 6x1.5L", "price": "4.99", "source": "Rewe", "link": "https://shop.rewe.de/coca-cola", "thumbnail": "", "product_id": "essen-rewe-7"},
    {"title": "Red Bull Energy Drink 4x250ml", "price": "5.49", "source": "Edeka", "link": "https://www.edeka.de/red-bull", "thumbnail": "", "product_id": "essen-edeka-4"},
    {"title": "Apfelsaft naturtrüb 1L", "price": "1.39", "source": "Rewe", "link": "https://shop.rewe.de/apfelsaft", "thumbnail": "", "product_id": "essen-rewe-8"},
    {"title": "Mineralwasser still 6x1.5L", "price": "3.29", "source": "Lidl", "link": "https://www.lidl.de/mineralwasser", "thumbnail": "", "product_id": "essen-lidl-2"},
    {"title": "Orangensaft frisch 1L", "price": "2.49", "source": "Rewe", "link": "https://shop.rewe.de/orangensaft", "thumbnail": "", "product_id": "essen-rewe-9"},
    {"title": "Fritz-Kola 24x0.33L", "price": "14.99", "source": "Rewe", "link": "https://shop.rewe.de/fritz-kola", "thumbnail": "", "product_id": "essen-rewe-10"},
    {"title": "Club Mate 12x0.5L", "price": "18.99", "source": "Getränkefachhandel", "link": "https://example.de/club-mate", "thumbnail": "", "product_id": "essen-getraenk-1"},
    {"title": "Tee Earl Grey 25 Beutel", "price": "2.99", "source": "DM", "link": "https://www.dm.de/tee", "thumbnail": "", "product_id": "essen-dm-2"},
    {"title": "Kaffee Bohnen 500g", "price": "6.99", "source": "Rewe", "link": "https://shop.rewe.de/kaffee", "thumbnail": "", "product_id": "essen-rewe-11"},
    # Obst & Gemüse
    {"title": "Äpfel Gala 1kg", "price": "2.49", "source": "Rewe", "link": "https://shop.rewe.de/aepfel", "thumbnail": "", "product_id": "essen-rewe-12"},
    {"title": "Bananen 1kg", "price": "1.49", "source": "Edeka", "link": "https://www.edeka.de/bananen", "thumbnail": "", "product_id": "essen-edeka-5"},
    {"title": "Orangen 2kg Netz", "price": "3.99", "source": "Rewe", "link": "https://shop.rewe.de/orangen", "thumbnail": "", "product_id": "essen-rewe-13"},
    {"title": "Weintrauben weiß 500g", "price": "2.99", "source": "Rewe", "link": "https://shop.rewe.de/weintrauben", "thumbnail": "", "product_id": "essen-rewe-14"},
    {"title": "Erdbeeren 500g", "price": "3.49", "source": "Edeka", "link": "https://www.edeka.de/erdbeeren", "thumbnail": "", "product_id": "essen-edeka-6"},
    {"title": "Karotten 1kg", "price": "1.19", "source": "Lidl", "link": "https://www.lidl.de/karotten", "thumbnail": "", "product_id": "essen-lidl-3"},
    {"title": "Gurke 1 Stück", "price": "0.79", "source": "Rewe", "link": "https://shop.rewe.de/gurke", "thumbnail": "", "product_id": "essen-rewe-15"},
    {"title": "Tomaten 500g", "price": "2.29", "source": "Rewe", "link": "https://shop.rewe.de/tomaten", "thumbnail": "", "product_id": "essen-rewe-16"},
    # Brot & Aufstrich
    {"title": "Vollkornbrot 500g", "price": "2.99", "source": "Rewe", "link": "https://shop.rewe.de/vollkornbrot", "thumbnail": "", "product_id": "essen-rewe-17"},
    {"title": "Brötchen 6er Pack", "price": "1.49", "source": "Edeka", "link": "https://www.edeka.de/broetchen", "thumbnail": "", "product_id": "essen-edeka-7"},
    {"title": "Frischkäse Kräuter 200g", "price": "1.79", "source": "Rewe", "link": "https://shop.rewe.de/frischkaese", "thumbnail": "", "product_id": "essen-rewe-18"},
    {"title": "Marmelade Erdbeere 450g", "price": "2.19", "source": "Rewe", "link": "https://shop.rewe.de/marmelade", "thumbnail": "", "product_id": "essen-rewe-19"},
    {"title": "Honig 500g", "price": "4.99", "source": "DM", "link": "https://www.dm.de/honig", "thumbnail": "", "product_id": "essen-dm-3"},
    # Hackathon / Event typisch
    {"title": "Pizza Margherita TK 400g", "price": "2.99", "source": "Rewe", "link": "https://shop.rewe.de/pizza-tk", "thumbnail": "", "product_id": "essen-rewe-20"},
    {"title": "Sandwich-Mix Party 20 Stück", "price": "12.99", "source": "Metro", "link": "https://www.metro.de/sandwich", "thumbnail": "", "product_id": "essen-metro-1"},
    {"title": "Müsliriegel 12er Pack", "price": "4.49", "source": "Rewe", "link": "https://shop.rewe.de/muesliriegel", "thumbnail": "", "product_id": "essen-rewe-21"},
    {"title": "Energie-Riegel 24er Box", "price": "14.99", "source": "DM", "link": "https://www.dm.de/energie-riegel", "thumbnail": "", "product_id": "essen-dm-4"},
    {"title": "Kekse gemischt 1kg", "price": "3.99", "source": "Rewe", "link": "https://shop.rewe.de/kekse", "thumbnail": "", "product_id": "essen-rewe-22"},
    {"title": "Kaffee Pads 36 Stück", "price": "5.99", "source": "Rewe", "link": "https://shop.rewe.de/kaffee-pads", "thumbnail": "", "product_id": "essen-rewe-23"},
    {"title": "Wasser 12x1L Still", "price": "4.49", "source": "Lidl", "link": "https://www.lidl.de/wasser", "thumbnail": "", "product_id": "essen-lidl-4"},
    {"title": "Obstkorb Büro 5kg", "price": "24.99", "source": "Obstkorb.de", "link": "https://example.de/obstkorb", "thumbnail": "", "product_id": "essen-obst-1"},
    {"title": "Brezen 10er Pack", "price": "6.99", "source": "Metro", "link": "https://www.metro.de/brezen", "thumbnail": "", "product_id": "essen-metro-2"},
    {"title": "Croissant 8er Pack", "price": "3.49", "source": "Rewe", "link": "https://shop.rewe.de/croissant", "thumbnail": "", "product_id": "essen-rewe-24"},
]


def _parse_price(price_str: str) -> float:
    """Aus Preis-String (z.B. '2.49' oder '2,49') float extrahieren."""
    if not price_str:
        return 0.0
    s = str(price_str).replace(",", ".").replace("€", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def search_essen(
    query: str,
    budget_min: float | None = None,
    budget_max: float | None = None,
    limit: int = 3,
) -> list[dict]:
    """
    Filtert die statischen Essen-Daten nach Suchbegriff und optional Budget.
    Rückgabe im SerpAPI-ähnlichen Format (title, link, price, source, thumbnail, product_id).
    """
    q_lower = (query or "").lower()
    # Suchbegriffe: einzelne Wörter für Treffer
    terms = [t for t in q_lower.split() if len(t) > 1]

    def matches(product: dict) -> bool:
        title = (product.get("title") or "").lower()
        source = (product.get("source") or "").lower()
        text = f"{title} {source}"
        if not terms:
            return True
        return any(t in text for t in terms)

    filtered = [p for p in ESSEN_PRODUKTE if matches(p)]
    out = []
    for p in filtered:
        price_val = _parse_price(p.get("price", "0"))
        if budget_min is not None and price_val < budget_min:
            continue
        if budget_max is not None and price_val > budget_max:
            continue
        # Kopie mit einheitlichen Keys (SerpAPI-kompatibel)
        out.append({
            "title": p.get("title", ""),
            "link": p.get("link", ""),
            "price": p.get("price", ""),
            "extracted_price": price_val,
            "source": p.get("source", ""),
            "thumbnail": p.get("thumbnail", ""),
            "product_id": p.get("product_id", ""),
        })
        if len(out) >= limit:
            break
    return out
