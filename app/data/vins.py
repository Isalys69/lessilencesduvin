import sqlite3
from pathlib import Path

# Définir le chemin absolu vers la base de données
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "vins.db"

def get_vins_par_couleur(couleur: str):
    """
    Retourne la liste des vins d'une couleur donnée depuis la base SQLite.

    Args:
        couleur (str): Nom de la catégorie ('Rouges', 'Blancs', 'Garde', etc.)

    Returns:
        list[dict]: Liste de dictionnaires contenant les informations de chaque vin.
    """

    query = """
        SELECT id, nom, domaine, millesime, prix, image, accord
        FROM vins
        WHERE LOWER(couleur) = LOWER(?)
        ORDER BY nom ASC;
    """

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # permet de récupérer les colonnes par nom
            cursor = conn.cursor()
            cursor.execute(query, (couleur,))
            rows = cursor.fetchall()
            vins = [dict(row) for row in rows]
            return vins

    except Exception as e:
        print(f"[ERREUR] Impossible de charger les vins {couleur} : {e}")
        return []
