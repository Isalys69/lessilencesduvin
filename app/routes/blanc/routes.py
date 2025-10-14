from flask import Blueprint, render_template
from app import get_db
from app.utils.panier_tools import get_compteur_panier


blanc_bp = Blueprint('blanc', __name__, url_prefix='/blanc')

@blanc_bp.route('/')
def index():
    db = get_db()
    vins = db.execute("SELECT * FROM vins WHERE couleur = 'Blanc'").fetchall()
    # 🔹 Calcul du compteur
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='Blanc', compteur=compteur)
