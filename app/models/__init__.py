"""
Initialisation du module models.

IMPORTANT:
- Ne JAMAIS appeler create_app() ici.
- Ne JAMAIS exécuter de logique DB à l'import (sinon effets de bord, logs doublés,
  instanciations multiples en CLI, etc.)
- Les checks doivent être appelés explicitement depuis create_app().
"""
import os
import logging
from sqlalchemy import inspect

logger = logging.getLogger(__name__)

def check_users_table(db):
    """
    Vérifie la présence de la table 'users'.

    - A appeler explicitement depuis create_app().
    - Ne s'exécute pas en CLI (trop bruyant + Flask CLI instancie l'app plusieurs fois).
    """
    is_cli = os.environ.get("FLASK_RUN_FROM_CLI") == "true"
    if is_cli:
        return

    try:
        inspector = inspect(db.engine)
        if "users" not in inspector.get_table_names():
            logger.warning(
                "⚠️ La table 'users' est absente de vins.db — exécutez db.create_all() pour la créer."
            )
        else:
            logger.info("✅ Table 'users' détectée dans vins.db.")
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la table users : {e}")