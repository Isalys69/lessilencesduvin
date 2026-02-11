"""
Routes du module blanc.
Affiche les vins blancs via SQLAlchemy (table vin).
"""
from flask import Blueprint, render_template
from app.models.vin import Vin
from app.utils.panier_tools import get_compteur_panier

blanc_bp = Blueprint('blanc', __name__, url_prefix='/blanc')

@blanc_bp.route('/')
def index():
    vins = (
        Vin.query
        .filter(Vin.couleur.ilike('blanc'))
        .order_by(Vin.nom.asc())
        .all()
    )
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='Blanc', compteur=compteur)
