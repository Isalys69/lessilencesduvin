"""
Initialisation du module models.
Vérifie la présence des tables essentielles dans la base de données.
"""
from app import db, create_app
from sqlalchemy import inspect
import logging

logger = logging.getLogger(__name__)

def check_users_table():
    try:
        app = create_app()
        with app.app_context():
            inspector = inspect(db.engine)
            if 'users' not in inspector.get_table_names():
                logger.warning("⚠️ La table 'users' est absente de vins.db — exécutez db.create_all() pour la créer.")
            else:
                logger.info("✅ Table 'users' détectée dans vins.db.")
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la table users : {e}")

# Exécuter le contrôle dès l'import
try:
    check_users_table()
except Exception as e:
    logger.error(f"Erreur d'initialisation models : {e}")
