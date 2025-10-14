# app/utils/panier_tools.py
from app.data.panier_data import PANIER

def get_compteur_panier():
    return sum(item.get('qty', 1) for item in PANIER)
