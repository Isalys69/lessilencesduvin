"""
Routes du module Contact.
Affiche la page contact.
"""

from flask import Blueprint, render_template

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')

@contact_bp.route('/')
def index():
    """Affiche la page du contact."""
    return render_template('contact.html')
