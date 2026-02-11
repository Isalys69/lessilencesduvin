"""
Routes du module garde.
Affiche une sélection "de garde" via SQLAlchemy (table vin).
Règle V1 : annee <= 2018.
"""
from flask import Blueprint, render_template
from app.models.vin import Vin
from app.utils.panier_tools import get_compteur_panier

garde_bp = Blueprint('garde', __name__, url_prefix='/garde')

@garde_bp.route('/')
def index():
    vins = (
        Vin.query
        .filter(Vin.annee.isnot(None))
        .filter(Vin.annee <= 2018)
        .order_by(Vin.nom.asc())
        .all()
    )
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='de garde', compteur=compteur)
