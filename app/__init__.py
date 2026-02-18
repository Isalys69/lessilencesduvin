"""
Initialisation principale de l'application Flask.
Gère la configuration, la base SQLite et l'enregistrement des Blueprints.
"""
import os
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
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "vins.db")



# ───────────────────────────────────────────
# 🧱 Factory principale Flask
# ───────────────────────────────────────────
def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

    
    # 📜 Logger (fichier + console)
    LOG_DIR = DATA_DIR
    LOG_PATH = os.path.join(LOG_DIR, "app.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # 🔌 DB — SQLAlchemy (source de vérité = config.Config)
    db.init_app(app)

    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
        logger.info("Connexion SQLAlchemy réussie")
    except Exception as e:
        logger.error(f"Erreur connexion SQLAlchemy : {e}")



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

    # ------------------------------------------------------
    # CONTEXT PROCESSOR GLOBAL : badge nouvelles commandes
    # ------------------------------------------------------
    from flask_login import current_user
    from app.models.commandes import Commande

    @app.context_processor
    def inject_commandes_badge():
        """Injecte le nombre de commandes complétées pour l'admin."""
        nb_commandes = 0
        try:
            if current_user.is_authenticated:
                nb_commandes = Commande.query.filter_by(statut="complétée").count()
        except Exception:
            nb_commandes = 0
        return dict(nb_nouvelles_commandes=nb_commandes)

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
    from app.routes.admin.routes import admin_bp

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
    app.register_blueprint(admin_bp)

    return app
