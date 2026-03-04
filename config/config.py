"""
Configuration centralisée de l'application Flask
Gère les environnements dev/prod et les variables sensibles
"""

import os
from datetime import timedelta
from dotenv import load_dotenv


# Charge les variables d'environnement depuis .env
# (ne casse pas si le fichier est absent)
load_dotenv()


class Config:
    """Configuration de base (commune à tous les environnements)"""

    # ═══════════════════════════════════════════════════════════
    # 🔐 SÉCURITÉ
    # ═══════════════════════════════════════════════════════════
    # SECRET_KEY est obligatoire pour Flask (sessions + CSRF)
    # On ne lève PAS d'erreur ici pour éviter de casser les imports
    SECRET_KEY = os.getenv("SECRET_KEY")

    # ═══════════════════════════════════════════════════════════
    # 💾 BASE DE DONNÉES
    # ═══════════════════════════════════════════════════════════
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    DB_PATH = os.path.join(DATA_DIR, "vins.db")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DB_PATH}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ═══════════════════════════════════════════════════════════
    # 🔒 SESSIONS (sécurité cookies)
    # ═══════════════════════════════════════════════════════════
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", 2))
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # SESSION_COOKIE_SECURE défini selon environnement

    # ═══════════════════════════════════════════════════════════
    # 📧 EMAIL (OVH)
    # ═══════════════════════════════════════════════════════════
    MAIL_SERVER = os.getenv("MAIL_SERVER", "ssl0.ovh.net")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() == "true"
    MAIL_USE_TLS = False

    # Liste des destinataires
    raw_recipients = os.getenv("MAIL_RECIPIENT", "")
    MAIL_RECIPIENT = [r.strip() for r in raw_recipients.split(",") if r.strip()]

    # Validation email minimale
    if MAIL_USERNAME and not MAIL_PASSWORD:
        raise ValueError(
            "❌ MAIL_PASSWORD manquant alors que MAIL_USERNAME est défini"
        )

    # ═══════════════════════════════════════════════════════════
    # 💳 STRIPE
    # ═══════════════════════════════════════════════════════════
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # En dev on tolère l'absence
    if not STRIPE_SECRET_KEY:
        print(
            "⚠️  ATTENTION : STRIPE_SECRET_KEY manquante "
            "(OK en dev, BLOQUANT en production)"
        )


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""

    DEBUG = True
    TESTING = False

    # HTTP autorisé en dev
    SESSION_COOKIE_SECURE = False

    # SQL logs optionnels
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""

    DEBUG = False
    TESTING = False

    # HTTPS obligatoire
    SESSION_COOKIE_SECURE = True

    # Validation Stripe obligatoire en prod
    if not Config.STRIPE_SECRET_KEY:
        raise ValueError(
            "❌ ERREUR CRITIQUE : STRIPE_SECRET_KEY manquante en PRODUCTION\n"
            "Le site ne peut pas accepter de paiements sans clé Stripe valide."
        )


# ═══════════════════════════════════════════════════════════
# 📌 Mapping des configurations
# ═══════════════════════════════════════════════════════════
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """
    Retourne la configuration appropriée selon FLASK_ENV.

    Utilisation :
        from config.config import get_config
        app.config.from_object(get_config())
    """

    env = os.getenv("FLASK_ENV", "development")
    return config.get(env, config["default"])