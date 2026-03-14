from functools import wraps
import os, stripe
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.vin import Vin
from app.models.domaine import Domaine
from app.models.commandes import Commande, CommandeProduit
from app.utils.stripe_tools import safe_refund, TRANSITIONS_ADMIN, LABELS_STATUT
from app.utils.email import send_plain_email

from app.extensions import csrf

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Décorateur : réserve la route aux utilisateurs is_admin=True."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/add-wine", methods=["GET", "POST"])
@login_required
@admin_required
@csrf.exempt
def add_wine():
    domaines = Domaine.query.order_by(Domaine.nom.asc()).all()

    if request.method == "POST":
        try:
            vin = Vin(
                nom=request.form["nom"].strip(),
                domaine_id=int(request.form["domaine_id"]),
                couleur=request.form["couleur"],
                annee=request.form.get("annee") or None,
                prix=float(str(request.form["prix"]).replace(",", ".")),
                stock=int(request.form["stock"]),
                photo=(request.form.get("photo") or "").strip() or None,
            )
            db.session.add(vin)
            db.session.commit()
            flash("✅ Vin ajouté avec succès.", "success")
            return redirect(url_for("admin.add_wine"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erreur lors de l'ajout du vin : {e}", "error")

    return render_template("admin/add_wine.html", domaines=domaines, user=current_user)


@admin_bp.route("/commandes", methods=["GET"])
@login_required
@admin_required
def commandes():
    commandes = Commande.query.order_by(Commande.date_commande.desc()).all()
    return render_template(
        "admin/commandes.html",
        commandes=commandes,
        transitions=TRANSITIONS_ADMIN,
        labels=LABELS_STATUT,
    )


@admin_bp.route("/commandes/<int:commande_id>/statut", methods=["POST"])
@login_required
@admin_required
@csrf.exempt
def changer_statut(commande_id):
    commande = Commande.query.get_or_404(commande_id)
    nouveau_statut = request.form.get("nouveau_statut", "").strip()

    transitions_autorisees = TRANSITIONS_ADMIN.get(commande.statut, [])
    if nouveau_statut not in transitions_autorisees:
        flash(f"❌ Transition {commande.statut} → {nouveau_statut} non autorisée.", "error")
        return redirect(url_for("admin.commandes"))

    if nouveau_statut == "annulée":
        ok, info = safe_refund(commande)
        if ok:
            flash(f"💳 Remboursement Stripe effectué (ref. {info}).", "success")
        elif commande.stripe_payment_intent_id:
            flash(f"⚠️ Remboursement échoué : {info}", "warning")
        # Annulation même si remboursement échoue (admin peut gérer manuellement)

    ancien_statut = commande.statut
    commande.statut = nouveau_statut
    db.session.commit()
    flash(f"✅ Commande #{commande_id} : {ancien_statut} → {nouveau_statut}.", "success")

    # Email client si adresse connue
    if commande.email_client and nouveau_statut in ("expédiée", "livrée", "annulée"):
        _notifier_client(commande, nouveau_statut)

    return redirect(url_for("admin.commandes"))


@admin_bp.route("/vins", methods=["GET"])
@login_required
@admin_required
def vins():
    tous_les_vins = Vin.query.join(Domaine).order_by(Domaine.nom.asc(), Vin.nom.asc()).all()
    return render_template("admin/vins.html", vins=tous_les_vins)


@admin_bp.route("/vins/<int:vin_id>/modifier", methods=["GET", "POST"])
@login_required
@admin_required
@csrf.exempt
def modifier_vin(vin_id):
    vin = Vin.query.get_or_404(vin_id)
    domaines = Domaine.query.order_by(Domaine.nom.asc()).all()

    if request.method == "POST":
        try:
            vin.nom        = request.form["nom"].strip()
            vin.domaine_id = int(request.form["domaine_id"])
            vin.couleur    = request.form["couleur"]
            vin.annee      = request.form.get("annee") or None
            vin.prix       = float(str(request.form["prix"]).replace(",", "."))
            vin.stock      = int(request.form["stock"])
            vin.photo      = (request.form.get("photo") or "").strip() or None
            vin.is_active  = "is_active" in request.form
            db.session.commit()
            flash("✅ Vin modifié avec succès.", "success")
            return redirect(url_for("admin.vins"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erreur lors de la modification : {e}", "error")

    return render_template("admin/modifier_vin.html", vin=vin, domaines=domaines)


@admin_bp.route("/vins/<int:vin_id>/supprimer", methods=["POST"])
@login_required
@admin_required
@csrf.exempt
def supprimer_vin(vin_id):
    vin = Vin.query.get_or_404(vin_id)
    dans_une_commande = CommandeProduit.query.filter_by(produit_id=vin_id).first()

    if dans_une_commande:
        vin.is_active = False
        db.session.commit()
        flash(f"⚠️ « {vin.nom} » désactivé du catalogue (commandes existantes conservées).", "warning")
    else:
        db.session.delete(vin)
        db.session.commit()
        flash(f"🗑️ « {vin.nom} » supprimé définitivement.", "success")

    return redirect(url_for("admin.vins"))


# ──────────────────────────────────────────────
# Helper privé : notification client par email
# ──────────────────────────────────────────────
def _notifier_client(commande, statut):
    from flask import current_app
    messages = {
        "expédiée": (
            f"Commande #{commande.id} expédiée – Les Silences du Vin",
            f"Bonjour,\n\nVotre commande #{commande.id} vient d'être expédiée.\n\n"
            f"Les Silences du Vin"
        ),
        "livrée": (
            f"Commande #{commande.id} livrée – Les Silences du Vin",
            f"Bonjour,\n\nNous espérons que vous avez bien reçu votre commande #{commande.id}.\n"
            f"Merci pour votre confiance !\n\nLes Silences du Vin"
        ),
        "annulée": (
            f"Commande #{commande.id} annulée – Les Silences du Vin",
            f"Bonjour,\n\nVotre commande #{commande.id} a été annulée.\n"
            f"Si un paiement avait été effectué, le remboursement a été initié.\n\n"
            f"Les Silences du Vin"
        ),
    }
    if statut not in messages:
        return
    subject, body = messages[statut]
    try:
        send_plain_email(
            subject=subject,
            body=body,
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[commande.email_client],
            reply_to="contact@lessilencesduvin.com",
        )
    except Exception as e:
        current_app.logger.error(
            f"[ADMIN] Email notif client commande {commande.id} ({statut}): {type(e).__name__} - {e}"
        )
