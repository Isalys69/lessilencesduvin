"""
Routes du module rouge.
Affiche les vins rouges depuis la base SQLite.
"""
from flask import Blueprint, render_template
from app import get_db
from app.utils.panier_tools import get_compteur_panier


rouge_bp = Blueprint('rouge', __name__, url_prefix='/rouge')

@rouge_bp.route('/')
def index():
    db = get_db()
    vins = db.execute("SELECT * FROM vins WHERE couleur = 'Rouge'").fetchall()
    compteur = get_compteur_panier()
    return render_template('vins_couleur.html', vins=vins, couleur='Rouge',compteur=compteur)
