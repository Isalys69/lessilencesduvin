# __init__.py – Initialisation de l’app Flask Les Silences du Vin

from flask import Flask, request, current_app
from flask_babel import Babel, _
import sqlite3, os

def create_app():
    app = Flask(__name__)

    # Configuration principale
    app.config['SECRET_KEY'] = 'remplace_moi_par_une_valeur_unique'
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    app.config["DATABASE"] = os.path.join(app.instance_path, "vins.db")
    os.makedirs(app.instance_path, exist_ok=True)

    # Debug : affichage du dossier de traduction utilisé
    print("TRAD DIR utilisé :", os.path.abspath(app.config['BABEL_TRANSLATION_DIRECTORIES']))

    
    # Sélecteur de langue (FR par défaut, IT possible)
    def select_locale():
        lang = request.args.get('lang')
        if lang in ('fr', 'it'):
            return lang
        return 'fr'

    # Initialisation de Babel
    babel = Babel(app, locale_selector=select_locale)

    # Filtre Jinja2 pour formatage des prix
    @app.template_filter('format_currency')
    def format_currency_filter(value):
        try:
            return "{:,.2f}".format(float(value)).replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return value

    # Rendre la fonction select_locale accessible aux templates
    app.jinja_env.globals['get_locale'] = select_locale

    # Importer les routes (après la création de app pour éviter les cycles)
    from app import routes
    app.register_blueprint(routes.bp)

    # Fonction utilitaire pour accéder à la BDD
    def get_db():
        db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
        return db



    return app


