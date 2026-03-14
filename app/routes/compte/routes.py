from flask import Blueprint, render_template, request, jsonify, session as flask_session, redirect, url_for, flash
from app.extensions import db
from app.models.commandes import Commande
from app.models.panier_sauvegarde import PanierSauvegarde
from flask_login import current_user, login_required
from datetime import datetime
from app.extensions import csrf
import json


compte_bp = Blueprint('compte', __name__, url_prefix='/compte')

@compte_bp.route('/commandes', methods=['GET', 'POST'])
@login_required
def commandes():

    STATUTS_EN_COURS = ("payé", "complétée", "en_préparation", "expédiée")
    commandes = Commande.query.filter(
        (
            (Commande.user_id == current_user.user_id) |
            (Commande.email_client == current_user.email)
        ),
        Commande.statut.in_(STATUTS_EN_COURS)
    ).order_by(Commande.date_commande.desc()).all()


    sauvegardes = PanierSauvegarde.query.filter(
        PanierSauvegarde.user_id == current_user.user_id
    ).order_by(PanierSauvegarde.date_creation.desc()).all()

    for s in sauvegardes:
    	s.panier = json.loads(s.contenu_json)

    return render_template(
		"account/commandes.html",
    	commandes=commandes,
    	sauvegardes=sauvegardes
    )

@compte_bp.route("/historique")
@login_required
def historique():

    STATUTS_TERMINES = ("livrée", "annulée")
    commandes = Commande.query.filter(
        (
            (Commande.user_id == current_user.user_id) |
            (Commande.email_client == current_user.email)
        ),
        Commande.statut.in_(STATUTS_TERMINES)
    ).order_by(Commande.date_commande.desc()).all()

    return render_template(
        "account/historique.html",
        commandes=commandes
    )

@compte_bp.route("/profil", methods=["GET", "POST"])
@csrf.exempt
@login_required
def profil():
    if request.method == "POST":
        current_user.nom       = request.form.get("nom", "").strip()
        current_user.prenom    = request.form.get("prenom", "").strip()
        current_user.email     = request.form.get("email", "").strip()
        current_user.updated_at = datetime.utcnow()

        db.session.commit()
        flash("Vos informations ont bien été mises à jour.", "success")
        return redirect(url_for("compte.profil"))

    return render_template("account/profil.html", user=current_user)


@compte_bp.route('/reprendre-commande/<int:commande_id>')
@login_required
def reprendre_commande(commande_id):
    commande = Commande.query.filter_by(
        id=commande_id,
        user_id=current_user.user_id,
        statut='payé'
    ).first_or_404()

    flask_session['commande_id'] = commande.id
    return redirect(url_for('paiement.infos_livraison'))
