"""
Initialisation principale de l'application Flask.
Gère la configuration, la base SQLite et l'enregistrement des Blueprints.
"""

import os
import sqlite3
from flask import Flask, g
from dotenv import load_dotenv

# ——————————————————————————————————————————
# 🔧 Chargement de la configuration
# ——————————————————————————————————————————
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))
DATABASE = os.path.join(os.path.dirname(__file__), "..", "vins.db")

# ——————————————————————————————————————————
# 🧱 Factory principale Flask
# ——————————————————————————————————————————
def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # ——————————————————————————————
    # 💾 Gestion de la base de données
    # ——————————————————————————————
    def get_db():
        """Retourne la connexion SQLite, attachée au contexte Flask."""
        if "db" not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        """Ferme la connexion SQLite à la fin de chaque requête."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ——————————————————————————————
    # 🔌 Enregistrement des Blueprints
    # ——————————————————————————————

    from app.routes.main import main_bp
    from app.routes.catalogue import catalogue_bp
    from app.routes.contact import contact_bp
    from app.routes.rouge import rouge_bp
    from app.routes.blanc import blanc_bp
    from app.routes.garde import garde_bp
    from app.routes.legales import legales_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(catalogue_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(rouge_bp)
    app.register_blueprint(blanc_bp)
    app.register_blueprint(garde_bp)
    app.register_blueprint(legales_bp)

    return app
