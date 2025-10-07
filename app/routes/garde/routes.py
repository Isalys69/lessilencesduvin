from flask import Blueprint, render_template
from app import get_db

garde_bp = Blueprint('garde', __name__, url_prefix='/garde')

@garde_bp.route('/')
def index():
    db = get_db()
    vins = db.execute("SELECT * FROM vins WHERE millesime <= 2018").fetchall()
    return render_template('vins_couleur.html', vins=vins, couleur='De garde')
