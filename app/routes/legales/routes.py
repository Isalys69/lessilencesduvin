from flask import Blueprint, render_template
from app.utils.panier_tools import get_compteur_panier

legales_bp = Blueprint('legales', __name__, url_prefix='/legales')

@legales_bp.route('/mentions')
def mentions():
    compteur = get_compteur_panier()
    return render_template('legales/mentions.html',compteur=compteur)

@legales_bp.route('/cgv')
def cgv():
    compteur = get_compteur_panier()
    return render_template('legales/cgv.html',compteur=compteur)

@legales_bp.route('/confidentialite')
def confidentialite():
    compteur = get_compteur_panier()
    return render_template('legales/confidentialite.html', compteur=compteur)
