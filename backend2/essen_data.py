"""
Essen-API (nur Quellcode): Realistische Mock-Daten für Lebensmittel-Suche.
Keine externe API – alle Daten stehen hier. Wird genutzt, wenn die Kategorie "food" ist.
Format der Einträge kompatibel zu SerpAPI shopping_results (title, link, price, source, thumbnail).
"""

# Real-life Style Produkte – wie von einer Essens-/Liefer-API
# Kategorien: snacks, getraenke, obst_gemuese, party_food, hackathon, suess, herzhaft
ESSEN_PRODUKTE = [
    # Snacks & Knabberzeug
    {"title": "Haribo Goldbären 5kg Eimer", "price": "€24,99", "extracted_price": 24.99, "source": "Amazon", "link": "https://example.com/essen/haribo", "thumbnail": "", "category": "snacks", "keywords": ["snacks", "süß", "party", "hackathon", "gummibärchen"]},
    {"title": "Pringles Original 6er Pack", "price": "€8,49", "extracted_price": 8.49, "source": "Rewe", "link": "https://example.com/essen/pringles", "thumbnail": "", "category": "snacks", "keywords": ["chips", "snacks", "party", "salzig"]},
    {"title": "Lorenz Crunchips Paprika 10x", "price": "€12,99", "extracted_price": 12.99, "source": "Edeka", "link": "https://example.com/essen/crunchips", "thumbnail": "", "category": "snacks", "keywords": ["chips", "snacks", "party"]},
    {"title": "Studentenfutter 1kg Mix", "price": "€9,99", "extracted_price": 9.99, "source": "DM", "link": "https://example.com/essen/studentenfutter", "thumbnail": "", "category": "snacks", "keywords": ["nüsse", "snacks", "gesund", "hackathon"]},
    {"title": "M&M's Erdnuss 3kg Beutel", "price": "€18,99", "extracted_price": 18.99, "source": "Metro", "link": "https://example.com/essen/mms", "thumbnail": "", "category": "snacks", "keywords": ["süß", "party", "snacks", "schokolade"]},
    {"title": "Bahlsen Leibniz Keks 1kg", "price": "€4,49", "extracted_price": 4.49, "source": "Rewe", "link": "https://example.com/essen/leibniz", "thumbnail": "", "category": "snacks", "keywords": ["keks", "snacks", "süß"]},
    {"title": "Erdnüsse geröstet 500g", "price": "€3,99", "extracted_price": 3.99, "source": "Aldi", "link": "https://example.com/essen/erdnuesse", "thumbnail": "", "category": "snacks", "keywords": ["nüsse", "snacks", "party"]},
    {"title": "Oreo Kekse 3er Pack", "price": "€3,29", "extracted_price": 3.29, "source": "Lidl", "link": "https://example.com/essen/oreo", "thumbnail": "", "category": "snacks", "keywords": ["keks", "süß", "snacks"]},
    # Getränke
    {"title": "Red Bull Energy 24er Dose", "price": "€42,99", "extracted_price": 42.99, "source": "Getränke Hoffmann", "link": "https://example.com/essen/redbull", "thumbnail": "", "category": "getraenke", "keywords": ["energy", "getränke", "hackathon", "party"]},
    {"title": "Coca-Cola Zero 24x0,33l", "price": "€14,99", "extracted_price": 14.99, "source": "Metro", "link": "https://example.com/essen/cola", "thumbnail": "", "category": "getraenke", "keywords": ["cola", "getränke", "party", "softdrink"]},
    {"title": "Apfelsaft 5l Bag-in-Box", "price": "€8,99", "extracted_price": 8.99, "source": "Rewe", "link": "https://example.com/essen/apfelsaft", "thumbnail": "", "category": "getraenke", "keywords": ["saft", "getränke", "party"]},
    {"title": "Mineralwasser 12x1,5l", "price": "€11,49", "extracted_price": 11.49, "source": "Edeka", "link": "https://example.com/essen/wasser", "thumbnail": "", "category": "getraenke", "keywords": ["wasser", "getränke", "party", "hackathon"]},
    {"title": "Club Mate 24er Kiste", "price": "€38,00", "extracted_price": 38.00, "source": "Getränkemarkt", "link": "https://example.com/essen/clubmate", "thumbnail": "", "category": "getraenke", "keywords": ["mate", "energy", "hackathon", "getränke"]},
    {"title": "Fritz-Kola 24er Kiste", "price": "€35,99", "extracted_price": 35.99, "source": "Amazon", "link": "https://example.com/essen/fritzkola", "thumbnail": "", "category": "getraenke", "keywords": ["cola", "getränke", "party", "hackathon"]},
    {"title": "Tee Beutel Grüntee 100 Stk", "price": "€6,99", "extracted_price": 6.99, "source": "DM", "link": "https://example.com/essen/tee", "thumbnail": "", "category": "getraenke", "keywords": ["tee", "getränke", "heiß"]},
    {"title": "Kaffee Bohnen 1kg", "price": "€12,99", "extracted_price": 12.99, "source": "Rewe", "link": "https://example.com/essen/kaffee", "thumbnail": "", "category": "getraenke", "keywords": ["kaffee", "getränke", "hackathon"]},
    # Obst & Gemüse
    {"title": "Äpfel Gala 2kg Netz", "price": "€3,49", "extracted_price": 3.49, "source": "Rewe", "link": "https://example.com/essen/aepfel", "thumbnail": "", "category": "obst_gemuese", "keywords": ["obst", "äpfel", "gesund", "snack"]},
    {"title": "Bananen 1,2kg Bund", "price": "€1,99", "extracted_price": 1.99, "source": "Edeka", "link": "https://example.com/essen/bananen", "thumbnail": "", "category": "obst_gemuese", "keywords": ["obst", "bananen", "gesund"]},
    {"title": "Karotten 1kg Bund", "price": "€1,29", "extracted_price": 1.29, "source": "Aldi", "link": "https://example.com/essen/karotten", "thumbnail": "", "category": "obst_gemuese", "keywords": ["gemüse", "karotten", "gesund"]},
    {"title": "Clementinen 2kg Netz", "price": "€4,99", "extracted_price": 4.99, "source": "Lidl", "link": "https://example.com/essen/clementinen", "thumbnail": "", "category": "obst_gemuese", "keywords": ["obst", "clementinen", "vitamine"]},
    {"title": "Trauben rot 500g", "price": "€2,99", "extracted_price": 2.99, "source": "Rewe", "link": "https://example.com/essen/trauben", "thumbnail": "", "category": "obst_gemuese", "keywords": ["obst", "trauben", "snack"]},
    # Party / Event
    {"title": "Pizza Tiefkühl 4er Pack", "price": "€7,99", "extracted_price": 7.99, "source": "Rewe", "link": "https://example.com/essen/pizza", "thumbnail": "", "category": "party_food", "keywords": ["pizza", "party", "herzhaft", "essen"]},
    {"title": "Mini-Salamis 200g Pack", "price": "€5,49", "extracted_price": 5.49, "source": "Edeka", "link": "https://example.com/essen/minisalami", "thumbnail": "", "category": "party_food", "keywords": ["party", "snacks", "herzhaft"]},
    {"title": "Käsewürfel Mix 400g", "price": "€6,99", "extracted_price": 6.99, "source": "Metro", "link": "https://example.com/essen/kaesewuerfel", "thumbnail": "", "category": "party_food", "keywords": ["käse", "party", "snacks"]},
    {"title": "Brezeln 10er Pack", "price": "€4,29", "extracted_price": 4.29, "source": "Backwerk", "link": "https://example.com/essen/brezeln", "thumbnail": "", "category": "party_food", "keywords": ["brezeln", "party", "snacks"]},
    {"title": "Sandwich-Platte fertig 20 Stk", "price": "€49,99", "extracted_price": 49.99, "source": "Metro", "link": "https://example.com/essen/sandwich", "thumbnail": "", "category": "party_food", "keywords": ["party", "catering", "sandwich"]},
    {"title": "Chips & Dips Set Party", "price": "€19,99", "extracted_price": 19.99, "source": "Amazon", "link": "https://example.com/essen/chipsdips", "thumbnail": "", "category": "party_food", "keywords": ["chips", "dips", "party", "snacks"]},
    # Hackathon-spezifisch
    {"title": "Snack-Box Hackathon 30 Pers", "price": "€89,00", "extracted_price": 89.00, "source": "Catering.de", "link": "https://example.com/essen/snackbox", "thumbnail": "", "category": "hackathon", "keywords": ["hackathon", "snacks", "party", "event", "catering"]},
    {"title": "Energy-Mix Büro 5kg", "price": "€34,99", "extracted_price": 34.99, "source": "Amazon", "link": "https://example.com/essen/energymix", "thumbnail": "", "category": "hackathon", "keywords": ["snacks", "hackathon", "büro", "nüsse", "süß"]},
    {"title": "Frühstücks-Set 20 Personen", "price": "€79,00", "extracted_price": 79.00, "source": "Metro", "link": "https://example.com/essen/fruehstueck", "thumbnail": "", "category": "hackathon", "keywords": ["frühstück", "hackathon", "catering", "event"]},
    {"title": "Badges & Snacks Bundle 60 Pers", "price": "€129,00", "extracted_price": 129.00, "source": "Event-Service", "link": "https://example.com/essen/badges", "thumbnail": "", "category": "hackathon", "keywords": ["hackathon", "badges", "snacks", "event"]},
    # Süß
    {"title": "Merci Schokolade 300g", "price": "€5,99", "extracted_price": 5.99, "source": "Rewe", "link": "https://example.com/essen/merci", "thumbnail": "", "category": "suess", "keywords": ["schokolade", "süß", "geschenk", "party"]},
    {"title": "Kinder Bueno 24er Pack", "price": "€14,99", "extracted_price": 14.99, "source": "Edeka", "link": "https://example.com/essen/bueno", "thumbnail": "", "category": "suess", "keywords": ["schokolade", "süß", "snacks"]},
    {"title": "Gummibärchen 1kg Mixed", "price": "€7,49", "extracted_price": 7.49, "source": "Lidl", "link": "https://example.com/essen/gummibaer", "thumbnail": "", "category": "suess", "keywords": ["gummibärchen", "süß", "snacks", "party"]},
    {"title": "Schokoladen-Kekse 800g", "price": "€4,99", "extracted_price": 4.99, "source": "Aldi", "link": "https://example.com/essen/schokokeks", "thumbnail": "", "category": "suess", "keywords": ["keks", "schokolade", "süß"]},
]


def _component_to_search_terms(component: dict) -> set:
    """Aus Plan-Komponente Suchbegriffe für Filterung ableiten."""
    terms = set()
    name = (component.get("name") or "").lower()
    notes = component.get("notes") or []
    for word in name.split():
        if len(word) > 2:
            terms.add(word)
    for note in notes:
        if isinstance(note, str):
            for w in note.lower().split():
                if len(w) > 2:
                    terms.add(w)
    # Kategorie-Mapping
    if "snack" in name or "snacks" in name or "snack" in str(notes).lower():
        terms.update(["snacks", "snack", "party", "hackathon", "süß", "chips", "nüsse"])
    if "getränk" in name or "drink" in name or "cola" in name or "energy" in name:
        terms.update(["getraenke", "getränke", "cola", "energy", "wasser", "kaffee"])
    if "party" in name or "event" in name:
        terms.update(["party", "party_food", "snacks", "getraenke"])
    if "hackathon" in name or "büro" in name:
        terms.update(["hackathon", "snacks", "getraenke", "energy", "kaffee"])
    if "obst" in name or "gesund" in name or "vitamin" in name:
        terms.update(["obst", "obst_gemuese", "gesund"])
    return terms


def _produkt_matches(p: dict, terms: set, budget_min: float, budget_max: float) -> bool:
    """Prüft, ob ein Produkt zu Suchbegriffen und Budget passt."""
    price = p.get("extracted_price") or 0
    if budget_max > 0 and price > budget_max:
        return False
    if budget_min > 0 and price < budget_min and budget_min < 100:  # Unterbudget nur ignorieren wenn Min sehr klein
        pass  # Unterbudget ok
    if not terms:
        return True
    title = (p.get("title") or "").lower()
    keywords = p.get("keywords") or []
    cat = (p.get("category") or "").lower()
    for term in terms:
        if term in title or term in cat or any(term in str(k).lower() for k in keywords):
            return True
    return False


def search_essen(component: dict, limit: int = 3) -> list[dict]:
    """
    Filtert die fest eingebauten Essens-Daten passend zur Plan-Komponente.
    Rückgabe im SerpAPI-ähnlichen Format (title, link, price, source, thumbnail)
    für Kompatibilität mit PlanComponentSearchOut.shopping_results.
    """
    terms = _component_to_search_terms(component)
    budget_min = float(component.get("budget_min") or 0)
    budget_max = float(component.get("budget_max") or 0)
    if budget_max <= 0:
        budget_max = 9999.0

    matches = [
        p for p in ESSEN_PRODUKTE
        if _produkt_matches(p, terms, budget_min, budget_max)
    ]
    # Sortierung: Preis aufsteigend, dann Relevanz (mehr Keyword-Treffer zuerst)
    def score(p):
        kw_match = sum(1 for k in (p.get("keywords") or []) if any(t in str(k).lower() for t in terms))
        return (-kw_match, p.get("extracted_price") or 0)
    matches.sort(key=score)

    # Nur Felder ausgeben, die Frontend/SerpAPI erwarten
    out = []
    for p in matches[:limit]:
        out.append({
            "title": p["title"],
            "link": p["link"],
            "price": p["price"],
            "extracted_price": p["extracted_price"],
            "source": p["source"],
            "thumbnail": p.get("thumbnail") or "",
        })
    return out
