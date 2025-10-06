"""
Routes du module Catalogue.
Affiche la page catalogue (liste des vins).
"""

from flask import Blueprint, render_template

catalogue_bp = Blueprint('catalogue', __name__, url_prefix='/catalogue')

@catalogue_bp.route('/')
def index():
    """Affiche la page du catalogue."""
    return render_template('catalogue.html')
