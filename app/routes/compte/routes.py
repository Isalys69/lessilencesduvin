from flask import Blueprint
from flask import render_template
from app.models.commandes import Commande
from app.models.panier_sauvegarde import PanierSauvegarde
from flask_login import current_user
import json


compte_bp = Blueprint('compte', __name__, url_prefix='/compte')

@compte_bp.route('/commandes', methods=['GET', 'POST'])
def commandes():

    commandes = Commande.query.filter(
        (
            (Commande.user_id == current_user.user_id) |
            (Commande.email_client == current_user.email)
        ),
        Commande.statut != "complétée"
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
def historique():

    commandes = Commande.query.filter(
        (
            (Commande.user_id == current_user.user_id) |
            (Commande.email_client == current_user.email)
        ),
        Commande.statut == "complétée"
    ).order_by(Commande.date_commande.desc()).all()

    return render_template(
        "account/historique.html",
        commandes=commandes
    )
    