"""
Initialisation principale de l'application Flask.
Gère la configuration, la base SQLite et l'enregistrement des Blueprints.
"""
import os
import sqlite3
import logging
from flask import Flask, g
from dotenv import load_dotenv

# ───────────────────────────────────────────
# 🔧 Config globale
# ───────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

# ✅ Chemin DB unique, au niveau module (ne le redéfinis pas plus bas)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vins.db")

# ───────────────────────────────────────────
# 💾 Fonctions DB accessibles partout
# ───────────────────────────────────────────
def get_db():
    """Retourne la connexion SQLite, attachée au contexte Flask."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(error=None):
    """Ferme la connexion SQLite à la fin de chaque requête."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ───────────────────────────────────────────
# 🧱 Factory principale Flask
# ───────────────────────────────────────────
def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # 📜 Logger (fichier + console)
    LOG_DIR = os.path.join(app.root_path, "data")
    LOG_PATH = os.path.join(LOG_DIR, "app.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 🔌 SQLite (V1) — on garde simple
    USE_SQLALCHEMY = False
    if USE_SQLALCHEMY:
        from flask_sqlalchemy import SQLAlchemy
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', f"sqlite:///{DB_PATH}"
        )
        db = SQLAlchemy(app)
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
            logger.info("Connexion SQLAlchemy réussie")
        except Exception as e:
            logger.error(f"Erreur connexion SQLAlchemy : {e}")
    else:
        # ✅ Enregistre le teardown pour la fermeture de connexion
        app.teardown_appcontext(close_db)
        # Petit test de connexion
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1")
            conn.close()
            logger.info(f"Connexion SQLite réussie ({DB_PATH})")
        except Exception as e:
            logger.error(f"Erreur connexion SQLite : {e}")

    # ───────────────────────────────────────
    # 🔌 Blueprints (inchangés)
    # ───────────────────────────────────────
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
