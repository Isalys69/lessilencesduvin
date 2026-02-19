
from flask import session
from decimal import Decimal, ROUND_HALF_UP

FREE_SHIPPING_THRESHOLD = Decimal("100.00")
SHIPPING_FEE = Decimal("9.90")

def compute_shipping(subtotal_eur: Decimal) -> Decimal:
    return Decimal("0.00") if subtotal_eur >= FREE_SHIPPING_THRESHOLD else SHIPPING_FEE

def money2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def get_session_panier():
    """Retourne le panier stocké dans la session, ou une liste vide."""
    return session.get('panier', [])

def set_session_panier(panier):
    """Enregistre le panier mis à jour dans la session."""
    session['panier'] = panier

def get_compteur_panier():
    """Calcule le nombre total de bouteilles dans le panier de la session."""
    panier = session.get('panier', [])
    return sum(item.get('qty', 1) for item in panier)
