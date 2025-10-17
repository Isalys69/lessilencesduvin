from flask import Blueprint, render_template
from app import get_db
from app.utils.panier_tools import get_compteur_panier


garde_bp = Blueprint('garde', __name__, url_prefix='/garde')

@garde_bp.route('/')
def index():
    db = get_db()
    vins = db.execute("SELECT * FROM vins WHERE millesime <= 2018").fetchall()
    # 🔹 Calcul du compteur
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='de garde', compteur=compteur)
