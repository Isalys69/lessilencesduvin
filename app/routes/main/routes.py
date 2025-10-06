"""
Routes principales (page d'accueil, navigation globale).
"""

from flask import Blueprint, render_template

TEMPLATE_ACCUEIL = "construction.html"  # deviendra "accueil.html" plus tard

# Création du Blueprint principal
main_bp = Blueprint('main', __name__)  # 👈 Nom unique du module

@main_bp.route('/')
def index():
    """Affiche la page d'accueil Les Silences du Vin."""
    return render_template(TEMPLATE_ACCUEIL)