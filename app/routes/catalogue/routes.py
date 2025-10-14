"""
Routes du module Catalogue.
Affiche la page catalogue (liste des vins).
"""

from flask import Blueprint, render_template
from app.utils.panier_tools import get_compteur_panier


catalogue_bp = Blueprint('catalogue', __name__, url_prefix='/catalogue')

@catalogue_bp.route('/')
def index():
    # 🔹 Calcul du compteur
    compteur = get_compteur_panier()

    #Affiche la page du catalogue.
    return render_template('catalogue.html', compteur=compteur)
