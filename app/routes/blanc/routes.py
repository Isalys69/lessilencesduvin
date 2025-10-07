from flask import Blueprint, render_template
from app import get_db

blanc_bp = Blueprint('blanc', __name__, url_prefix='/blanc')

@blanc_bp.route('/')
def index():
    db = get_db()
    vins = db.execute("SELECT * FROM vins WHERE couleur = 'Blanc'").fetchall()
    return render_template('vins_couleur.html', vins=vins, couleur='Blanc')
