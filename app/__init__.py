# __init__.py – Initialisation de l’app Flask Les Silences du Vin

from flask import Flask, request
from flask_babel import Babel
from flask_babel import _
import os

# Création de l’app Flask
app = Flask(__name__)

# Configuration principale de l’app
app.config['SECRET_KEY'] = 'remplace_moi_par_une_valeur_unique'
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Affichage du dossier de traduction utilisé (utile pour debug)
print("TRAD DIR utilisé :", os.path.abspath(app.config['BABEL_TRANSLATION_DIRECTORIES']))

# Sélecteur de langue pour Flask-Babel (ici FR ou IT, sinon FR par défaut)
def select_locale():
    lang = request.args.get('lang')
    if lang in ('fr', 'it'):
        return lang
    return 'fr'

# Initialisation de Flask-Babel
babel = Babel(app, locale_selector=select_locale)

# Déclaration d’un filtre personnalisé Jinja2 pour formater un prix en euros (ex : 12.9 -> 12,90)
@app.template_filter('format_currency')
def format_currency_filter(value):
    """
    Formate un prix en euros : 12.9 -> 12,90
    Utilisé dans les templates Jinja2 avec |format_currency
    """
    try:
        return "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value

# Rendre la fonction select_locale accessible dans tous les templates Jinja2
app.jinja_env.globals['get_locale'] = select_locale

# Importation des routes à la fin (pour éviter les import cycles)
from app import routes
