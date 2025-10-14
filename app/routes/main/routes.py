"""
Routes principales (page d'accueil, navigation globale).
"""

from flask import Blueprint, render_template
from app.utils.panier_tools import get_compteur_panier

TEMPLATE_ACCUEIL = "construction.html"  # deviendra "accueil.html" plus tard

# Création du Blueprint principal
main_bp = Blueprint('main', __name__)  # 👈 Nom unique du module

@main_bp.route('/')
def index():
    compteur = get_compteur_panier()
    return render_template(TEMPLATE_ACCUEIL, compteur=compteur)
