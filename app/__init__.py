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
from config.config import get_config
from sqlalchemy import text
from flask_wtf.csrf import CSRFProtect
from app.extensions import db, login_manager, csrf


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
    app.config.from_object(get_config())
    app.config["APP_VERSION"] = os.getenv("APP_VERSION", "dev")
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']

    # CSRF global (après création app + config)
    csrf.init_app(app)

    # 🔌 DB — SQLAlchemy (source de vérité = config.Config)
    db.init_app(app)

    # Login manager (config + init)
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page 💾"
    login_manager.login_message_category = "warning"
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.init_app(app)

    
    # 📜 Logger (fichier + console)
    LOG_DIR = DATA_DIR
    LOG_PATH = os.path.join(LOG_DIR, "app.log")
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)

    # Évite d'empiler plusieurs handlers si create_app() est appelé plusieurs fois
    # (cas fréquent avec Flask CLI / reloader). Sans ça, logs dupliqués.
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

    # Évite la propagation vers le root logger (sinon double log possible)
    logger.propagate = False


    # Petit check de connectivité DB utile au démarrage web,
    # mais trop bruyant côté CLI (Flask peut construire l'app plusieurs fois).
    # On ne le fait que si on tourne comme serveur web.
    is_cli = os.environ.get("FLASK_RUN_FROM_CLI") == "true"

    if not is_cli:
        try:
            with app.app_context():
                db.session.execute(text("SELECT 1"))
            logger.info("Connexion SQLAlchemy réussie")
        except Exception as e:
            logger.error(f"Erreur connexion SQLAlchemy : {e}")


    # Self-check DB (web uniquement, pas CLI) : présence table users
    # (Ne doit pas s'exécuter en CLI, sinon bruit + instanciations multiples)
    if not is_cli:
        from app.models import check_users_table
        with app.app_context():
            check_users_table(db)


    # ───────────────────────────────────────
    # 🧹 BLOC 5 — Hygiène des commandes en_attente
    # ------------------------------------------------------
    # Objectif métier :
    # Éviter que des commandes créées mais jamais payées
    # restent indéfiniment en base.
    #
    # Règle :
    # Si statut = "en_attente"
    # ET date_commande < now - X heures
    # → statut = "abandonnee"
    # → date_abandon = now
    # → abandon_motif = "ttl_expired"
    #
    # Garanties :
    # - Ne touche jamais aux commandes "payé", "complétée", etc.
    # - N’impacte pas le stock (non décrémenté à ce stade)
    # - Idempotent : une commande déjà basculée ne sera jamais retraitée
    # - Possibilité de simulation via --dry-run
    #
    # Usage :
    #   flask mark_abandoned_orders --hours 24
    #   flask mark_abandoned_orders --hours 24 --dry-run
    # ------------------------------------------------------

    import click
    from datetime import datetime, timedelta    
    from app.models.commandes import Commande

    @app.cli.command("mark_abandoned_orders")
    @click.option(
        "--hours",
        default=24,
        type=int,
        show_default=True,
        help="Seuil d'expiration en heures avant abandon."
    )
    @click.option(
        "--dry-run",
        is_flag=True,
        help="Simule l'opération sans modifier la base de données."
    )

    @click.option(
        "--limit",
        default=500,
        type=int,
        show_default=True,
        help="Nombre max de commandes traitées par exécution (sécurité V1)."
    )
    @click.option(
        "--batch-size",
        default=200,
        type=int,
        show_default=True,
        help="Taille des lots chargés en mémoire."
    )






    def mark_abandoned_orders(hours, dry_run, limit, batch_size):        
        """
        Commande CLI Flask.
        Marque comme 'abandonnee' les commandes 'en_attente'
        dont la date_commande dépasse le seuil défini.
        """

        # Sécurité minimale : éviter seuil incohérent
        if hours <= 0:
            click.echo("❌ --hours doit être strictement supérieur à 0.")
            return

        # Calcul du seuil temporel en UTC
        # (cohérent avec date_commande=datetime.utcnow())
        threshold = datetime.utcnow() - timedelta(hours=hours)

        # Requête ciblée :
        # On sélectionne UNIQUEMENT les commandes encore en attente
        # et dont la date est antérieure au seuil.
        query = Commande.query.filter(
            Commande.statut == "en_attente",
            Commande.date_commande < threshold
        )

        # On limite volontairement pour éviter qu'une erreur de seuil
        # (ou un cron trop fréquent) ne bascule massivement trop de lignes d'un coup.
        if limit <= 0:
            click.echo("❌ --limit doit être > 0")
            return
        if batch_size <= 0:
            click.echo("❌ --batch-size doit être > 0")
            return

        # Note : SQLite n'aime pas les grosses opérations concurrentes.
        # On traite par lots, et on garde une borne "limit" globale.
        commandes = (
            query.order_by(Commande.id.asc())
                 .limit(limit)
                 .yield_per(batch_size)
        )

        # Dry-run : on parcourt sans écrire
        if dry_run:
            shown = 0
            total_seen = 0
            click.echo(
                f"🧾 Dry-run: jusqu'à {limit} commande(s) max "
                f"(seuil={hours}h, avant {threshold.isoformat()} UTC)"
            )
            for c in commandes:
                total_seen += 1
                if shown < 20:
                    click.echo(
                        f" - id={c.id} | date_commande={c.date_commande} "
                        f"| stripe_session_id={c.stripe_session_id}"
                    )
                    shown += 1
            if total_seen == 0:
                click.echo("✅ 0 commande à abandonner.")
            elif total_seen > 20:
                click.echo(f"... (+{total_seen - 20} autres)")
            click.echo("✅ Dry-run terminé. Aucune modification effectuée.")
            return

        # Exécution réelle
        now = datetime.utcnow()
        changed = 0

        for c in commandes:
            # garde défensive
            if c.statut != "en_attente":
                continue
            c.statut = "abandonnee"
            c.date_abandon = now
            c.abandon_motif = "ttl_expired"
            changed += 1

        db.session.commit()

        logger.info(
            f"[BLOC5] mark_abandoned_orders changed={changed} "
            f"hours={hours} threshold={threshold.isoformat()}Z "
            f"limit={limit} batch_size={batch_size}"
        )

        click.echo(f"✅ {changed} commande(s) marquée(s) 'abandonnee'.")
        # Exécution réelle
        now = datetime.utcnow()
        changed = 0

        for c in commandes:

            # Garde métier défensive (double sécurité)
            # Même si la requête filtre déjà, on protège
            # contre toute modification concurrente.
            if c.statut != "en_attente":
                continue

            c.statut = "abandonnee"
            c.date_abandon = now
            c.abandon_motif = "ttl_expired"
            changed += 1

        # Commit unique (transaction groupée)
        db.session.commit()

        # Log applicatif pour traçabilité (audit minimal)
        logger.info(
            f"[BLOC5] mark_abandoned_orders "
            f"changed={changed} "
            f"hours={hours} "
            f"threshold={threshold.isoformat()}Z"
        )

        click.echo(f"✅ {changed} commande(s) marquée(s) 'abandonnee'.")





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
    from app.routes.compte.routes import compte_bp

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
    app.register_blueprint(compte_bp)

    return app
