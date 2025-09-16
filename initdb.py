import sqlite3
from pathlib import Path

db_path = Path("instance/vins.db")
db_path.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Table unique
c.execute("""
CREATE TABLE IF NOT EXISTS vins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    millesime INTEGER,
    prix REAL,
    accord TEXT
)
""")

# Donnée test : Auxerrois 2022
c.execute("""
INSERT INTO vins (nom, millesime, prix, accord)
VALUES (?, ?, ?, ?)
""", ("Auxerrois", 2022, 15.0, "Poisson grillé"))

conn.commit()
conn.close()
