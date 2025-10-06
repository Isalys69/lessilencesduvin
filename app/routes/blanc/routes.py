"""
Routes du module blanc.
Affiche la page des vins blanc.
"""

from flask import Blueprint, render_template

blanc_bp = Blueprint('blanc', __name__, url_prefix='/blanc')

@blanc_bp.route('/')
def index():
    """Affiche la page du blanc."""
    return render_template('blanc.html')
