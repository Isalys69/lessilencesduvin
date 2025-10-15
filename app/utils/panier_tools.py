
from flask import session

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
