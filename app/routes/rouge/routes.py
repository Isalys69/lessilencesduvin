"""
Routes du module rouge.
Affiche la page des vins rouge.
"""

from flask import Blueprint, render_template

rouge_bp = Blueprint('rouge', __name__, url_prefix='/rouge')

@rouge_bp.route('/')
def index():
    """Affiche la page du rouge."""
    return render_template('rouge.html')
