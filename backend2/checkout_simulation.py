"""Simulierter Checkout: eine Adresse/Zahlung, Schritte pro Händler (Sandbox)."""
from models import ShoppingSession
from schemas import CheckoutStepOut, CheckoutSimulationOut


def run_checkout_simulation(session: ShoppingSession) -> CheckoutSimulationOut:
    """
    Erzeugt einen simulierten Checkout-Ablauf:
    - Zahlung und Adresse einmal eingegeben (konzeptionell).
    - Pro Händler ein oder mehrere Schritte (simuliert).
    """
    retailer_ids = list({item.retailer_id for item in session.cart_items})
    steps: list[CheckoutStepOut] = []
    step_num = 1
    for rid in retailer_ids:
        description = f"Checkout bei {rid} – Adresse & Zahlung übernommen (Simulation)."
        steps.append(CheckoutStepOut(
            retailer_id=rid,
            step_number=step_num,
            description=description,
            url=f"https://checkout-sandbox.example.com/{rid}",
            status="simulated_done",
        ))
        step_num += 1

    return CheckoutSimulationOut(
        session_id=session.id,
        payment_entered_once=True,
        address_entered_once=True,
        steps=steps,
        message="Checkout ist simuliert – keine echte Zahlung. Der Agent würde pro Händler den Checkout mit deinen Daten ausführen.",
    )
