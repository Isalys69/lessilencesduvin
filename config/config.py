"""
Configuration centralisée de l'application Flask
Gère les environnements dev/prod et les variables sensibles
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env
load_dotenv()


class Config:
    """Configuration de base (commune à tous les environnements)"""
    
    # ═══════════════════════════════════════════════════════════
    # 🔐 SÉCURITÉ (SECRET_KEY obligatoire)
    # ═══════════════════════════════════════════════════════════
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "❌ ERREUR CRITIQUE : SECRET_KEY manquante dans le fichier .env\n"
            "   Générez-en une avec : python3 -c \"import secrets; print(secrets.token_hex(32))\""
        )
    
    # ═══════════════════════════════════════════════════════════
    # 💾 BASE DE DONNÉES
    # ═══════════════════════════════════════════════════════════
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'app', 'data', 'vins.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ═══════════════════════════════════════════════════════════
    # 🔒 SESSIONS (sécurité des cookies)
    # ═══════════════════════════════════════════════════════════
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", 2))
    )
    SESSION_COOKIE_HTTPONLY = True  # Protection XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF
    # SESSION_COOKIE_SECURE sera défini selon l'environnement (dev/prod)
    
    # ═══════════════════════════════════════════════════════════
    # 📧 CONFIGURATION EMAIL (OVH)
    # ═══════════════════════════════════════════════════════════
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'ssl0.ovh.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USE_TLS = False  # SSL et TLS sont mutuellement exclusifs
    
    # Liste des destinataires (séparés par des virgules dans .env)
    raw_recipients = os.getenv('MAIL_RECIPIENT', '')
    MAIL_RECIPIENT = [r.strip() for r in raw_recipients.split(',') if r.strip()]
    
    # Validation : si username défini, password doit l'être aussi
    if MAIL_USERNAME and not MAIL_PASSWORD:
        raise ValueError("❌ MAIL_PASSWORD manquant alors que MAIL_USERNAME est défini")
    
    # ═══════════════════════════════════════════════════════════
    # 💳 STRIPE (paiements)
    # ═══════════════════════════════════════════════════════════
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # En développement, les clés test sont OK
    # En production, elles sont obligatoires
    if not STRIPE_SECRET_KEY:
        print("⚠️  ATTENTION : STRIPE_SECRET_KEY manquante (OK en dev, BLOQUANT en prod)")


class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # HTTP autorisé en dev (localhost)
    
    # Logs plus verbeux en dev
    SQLALCHEMY_ECHO = False  # Mettre True pour voir les requêtes SQL


class ProductionConfig(Config):
    """Configuration pour l'environnement de production"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS OBLIGATOIRE en production
    
    # Validation stricte en production
    if not Config.STRIPE_SECRET_KEY:
        raise ValueError(
            "❌ ERREUR CRITIQUE : STRIPE_SECRET_KEY manquante en PRODUCTION\n"
            "   Le site ne peut pas accepter de paiements sans clé Stripe valide."
        )


# ═══════════════════════════════════════════════════════════
# 📌 Dictionnaire des configurations
# ═══════════════════════════════════════════════════════════
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Retourne la configuration appropriée selon la variable FLASK_ENV
    
    Usage dans __init__.py :
        from config.config import get_config
        app.config.from_object(get_config())
    """
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])