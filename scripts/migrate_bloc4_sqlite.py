import os
import shutil
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("app/data", "vins.db")

def table_exists(cur, name: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None

def column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cur.fetchall()]  # row[1] = name
    return column in cols

def index_exists(cur, name: str) -> bool:
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?;", (name,))
    return cur.fetchone() is not None

def backup_db(db_path: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{ts}"
    shutil.copy2(db_path, backup_path)
    return backup_path

def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"DB introuvable: {DB_PATH}")

    backup_path = backup_db(DB_PATH)
    print(f"✅ Backup créé: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON;")
    cur = conn.cursor()

    try:
        # -------------------------------------------------------
        # 1) Ajouter les colonnes Stripe + refund à la table commandes
        # -------------------------------------------------------
        if not table_exists(cur, "commandes"):
            raise SystemExit("Table 'commandes' introuvable. Vérifie que tu pointes la bonne DB.")

        # stripe_payment_intent_id
        if not column_exists(cur, "commandes", "stripe_payment_intent_id"):
            cur.execute("ALTER TABLE commandes ADD COLUMN stripe_payment_intent_id VARCHAR(255);")
            print("➕ Ajout colonne: commandes.stripe_payment_intent_id")

        # refund_effectue (bool)
        if not column_exists(cur, "commandes", "refund_effectue"):
            # SQLite n'a pas de vrai BOOL -> INTEGER 0/1
            cur.execute("ALTER TABLE commandes ADD COLUMN refund_effectue INTEGER NOT NULL DEFAULT 0;")
            print("➕ Ajout colonne: commandes.refund_effectue")

        # stripe_refund_id
        if not column_exists(cur, "commandes", "stripe_refund_id"):
            cur.execute("ALTER TABLE commandes ADD COLUMN stripe_refund_id VARCHAR(255);")
            print("➕ Ajout colonne: commandes.stripe_refund_id")

        # date_refund
        if not column_exists(cur, "commandes", "date_refund"):
            cur.execute("ALTER TABLE commandes ADD COLUMN date_refund DATETIME;")
            print("➕ Ajout colonne: commandes.date_refund")

        # Index utiles sur commandes
        if not index_exists(cur, "ix_commandes_stripe_payment_intent_id"):
            cur.execute("CREATE INDEX ix_commandes_stripe_payment_intent_id ON commandes(stripe_payment_intent_id);")
            print("📌 Création index: ix_commandes_stripe_payment_intent_id")

        if not index_exists(cur, "ix_commandes_stripe_refund_id"):
            cur.execute("CREATE INDEX ix_commandes_stripe_refund_id ON commandes(stripe_refund_id);")
            print("📌 Création index: ix_commandes_stripe_refund_id")

        # -------------------------------------------------------
        # 2) Créer table stripe_events (idempotence event.id)
        # -------------------------------------------------------
        if not table_exists(cur, "stripe_events"):
            cur.execute("""
                CREATE TABLE stripe_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id VARCHAR(255) NOT NULL,
                    event_type VARCHAR(255),
                    stripe_session_id VARCHAR(255),
                    commande_id INTEGER,
                    created_at DATETIME NOT NULL
                );
            """)
            print("🧱 Création table: stripe_events")

        # Unique + index sur event_id
        # (SQLite: on fait un unique index explicite)
        if not index_exists(cur, "ux_stripe_events_event_id"):
            cur.execute("CREATE UNIQUE INDEX ux_stripe_events_event_id ON stripe_events(event_id);")
            print("🔐 Création unique index: ux_stripe_events_event_id")

        if not index_exists(cur, "ix_stripe_events_stripe_session_id"):
            cur.execute("CREATE INDEX ix_stripe_events_stripe_session_id ON stripe_events(stripe_session_id);")
            print("📌 Création index: ix_stripe_events_stripe_session_id")

        if not index_exists(cur, "ix_stripe_events_commande_id"):
            cur.execute("CREATE INDEX ix_stripe_events_commande_id ON stripe_events(commande_id);")
            print("📌 Création index: ix_stripe_events_commande_id")

        conn.commit()
        print("✅ Migration Bloc 4 appliquée avec succès.")

    except Exception as e:
        conn.rollback()
        print("❌ ERREUR migration, rollback effectué.")
        print(f"   {type(e).__name__}: {e}")
        print(f"   Backup dispo: {backup_path}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()