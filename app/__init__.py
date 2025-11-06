"""
Initialisation principale de l'application Flask.
Gère la configuration, la base SQLite et l'enregistrement des Blueprints.
"""
import os
import sqlite3
import logging
from flask import Flask, g, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from config.config import Config
from sqlalchemy import text


# ───────────────────────────────────────────
# 📦 Extensions globales (V3)
# ───────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page 💾"
login_manager.login_message_category = "warning"


# ───────────────────────────────────────────
# 🔧 Config globale
# ───────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))

# Chemin DB unique, au niveau module (ne le redéfinis pas plus bas)
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vins.db")


# ───────────────────────────────────────────
# 💾 Fonctions DB (compatibilité V1 / V2)
# ───────────────────────────────────────────
def get_db():
    """Retourne la connexion SQLite, attachée au contexte Flask."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(error=None):
    """Ferme la connexion SQLite à la fin de chaque requête."""
    db_conn = g.pop("db", None)
    if db_conn is not None:
        db_conn.close()


# ───────────────────────────────────────────
# 🧱 Factory principale Flask
# ───────────────────────────────────────────
def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

    
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

    # 🔌 SQLite (V1) — on garde simple, mais on prépare V3
    USE_SQLALCHEMY = True  # Activation SQLAlchemy pour V3
    if USE_SQLALCHEMY:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', f"sqlite:///{DB_PATH}"
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            logger.info("Connexion SQLAlchemy réussie")
        except Exception as e:
            logger.error(f"Erreur connexion SQLAlchemy : {e}")
    else:
        app.teardown_appcontext(close_db)
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("SELECT 1")
            conn.close()
            logger.info(f"Connexion SQLite réussie ({DB_PATH})")
        except Exception as e:
            logger.error(f"Erreur connexion SQLite : {e}")

    # ───────────────────────────────────────
    # 🌐 Redirection HTTP → HTTPS
    # ───────────────────────────────────────
    @app.before_request
    def force_https():
        if not request.host.startswith("127.0.0.1") and request.url.startswith("http://"):
            https_url = request.url.replace("http://", "https://", 1)
            return redirect(https_url, code=301)

    # ------------------------------------------------------
    # CONTEXT PROCESSOR GLOBAL : compteur du panier
    # ------------------------------------------------------
    from app.utils.panier_tools import get_compteur_panier
    @app.context_processor
    def inject_panier_count():
        """Injecte automatiquement le compteur de panier dans tous les templates."""
        try:
            panier_count = get_compteur_panier()
        except Exception:
            panier_count = 0
        return dict(panier_count=panier_count)

    # ───────────────────────────────────────
    # 🔐 Authentification (Flask-Login)
    # ───────────────────────────────────────
    from app.models.user import User  # le modèle User sera défini dans G3R1C1
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.init_app(app)


    # ───────────────────────────────────────
    # 🔌 Blueprints 
    # ───────────────────────────────────────
    from app.routes.main import main_bp
    from app.routes.catalogue import catalogue_bp
    from app.routes.contact import contact_bp
    from app.routes.rouge import rouge_bp
    from app.routes.blanc import blanc_bp
    from app.routes.garde import garde_bp
    from app.routes.legales import legales_bp
    from app.routes.panier import panier_bp
    from app.routes.vins import vins_bp
    from app.routes.auth import auth_bp
    from app.routes.paiement import paiement_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(catalogue_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(rouge_bp)
    app.register_blueprint(blanc_bp)
    app.register_blueprint(garde_bp)
    app.register_blueprint(legales_bp)
    app.register_blueprint(panier_bp)
    app.register_blueprint(vins_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(paiement_bp)

    return app
