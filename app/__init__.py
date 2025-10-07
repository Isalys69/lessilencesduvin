"""
Initialisation principale de l'application Flask.
Gère la configuration, la base SQLite et l'enregistrement des Blueprints.
"""
import os
from flask import Flask
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
    # 💾 Gestion de la base de données (avec logging)
    # ——————————————————————————————
    import sqlite3
    import logging
    from flask import g

    # ——————————————————————————————
    # 📜 Configuration du logger
    # ——————————————————————————————
    LOG_DIR = os.path.join(app.root_path, "data")
    LOG_PATH = os.path.join(LOG_DIR, "app.log")

    # ✅ Création automatique du dossier si manquant
    os.makedirs(LOG_DIR, exist_ok=True)

    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger(__name__)

    # (optionnel) affichage console pendant le dev
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)


    # ——————————————————————————————
    # 💾 Gestion DB
    # ——————————————————————————————
    USE_SQLALCHEMY = False  # Passera à True lors de la migration MySQL

    if USE_SQLALCHEMY:
        from flask_sqlalchemy import SQLAlchemy

        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 'sqlite:///app/data/vins.db'
        )
        db = SQLAlchemy(app)

        # Test de connexion SQLAlchemy (MySQL ou SQLite)
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
            logger.info("Connexion SQLAlchemy réussie")
        except Exception as e:
            logger.error(f"Erreur connexion SQLAlchemy : {e}")

    else:
        DATABASE = os.path.join(app.root_path, "data", "vins.db")

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

        # Test de connexion SQLite
        try:
            conn = sqlite3.connect(DATABASE)
            conn.execute("SELECT 1")
            conn.close()
            logger.info(f"Connexion SQLite réussie ({DATABASE})")
        except Exception as e:
            logger.error(f"Erreur connexion SQLite : {e}")

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
