"""
Routes du module rouge.
Affiche les vins rouges via SQLAlchemy (table vin).
"""
from flask import Blueprint, render_template
from app.models.vin import Vin
from app.utils.panier_tools import get_compteur_panier

rouge_bp = Blueprint('rouge', __name__, url_prefix='/rouge')

@rouge_bp.route('/')
def index():
    vins = (
        Vin.query
        .filter(Vin.couleur.ilike('rouge'))
        .order_by(Vin.nom.asc())
        .all()
    )
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='Rouge', compteur=compteur)
