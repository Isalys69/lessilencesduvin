"""
Routes du module garde.
Affiche la page des vins de garde.
"""

from flask import Blueprint, render_template

garde_bp = Blueprint('garde', __name__, url_prefix='/garde')

@garde_bp.route('/')
def index():
    """Affiche la page du garde."""
    return render_template('garde.html')
