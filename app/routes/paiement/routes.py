import os, stripe
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session as flask_session, redirect, url_for, flash
from flask_login import current_user

from app import db
from app.models.commandes import Commande, CommandeProduit
from app.forms.checkout import GuestCheckoutForm
from app.utils.panier_tools import get_session_panier

# ======================================================
# 🧭 Blueprint Paiement
# ------------------------------------------------------
# Gère :
#   - la création de commande (checkout)
#   - la session Stripe
#   - le webhook de confirmation
#   - les pages de succès / annulation
# ======================================================
paiement_bp = Blueprint('paiement', __name__, url_prefix='/paiement')

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
print("✅ Stripe chargé - clé publique :", os.getenv("STRIPE_PUBLIC_KEY")[:15], "...")

# ======================================================
# 🟢 /paiement/create-checkout-session
# ------------------------------------------------------
# ➜ Crée une commande “en attente” avant le paiement Stripe
# ➜ Lance la session Stripe
# ➜ Associe la commande à la session Stripe (pour suivi du paiement)
# ➜ Redirige ensuite vers Stripe Checkout
# ======================================================

@paiement_bp.route('/create-checkout-session', methods=['POST', 'GET'])
def create_checkout_session():
    panier = get_session_panier()
    if not panier:
        flash("Votre panier est vide.", "warning")
        return redirect(url_for('catalogue.index'))

    total = sum(i['prix'] * i['qty'] for i in panier)
    montant_cents = int(float(total) * 100)

    # Détection de l’environnement (local ou production)
    if request.host.startswith("127.0.0.1") or "localhost" in request.host:
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = "https://www.lessilencesduvin.fr"

    # =====================================================
    # 🧾 Étape 1 : Création d'une commande "en attente"
    # -----------------------------------------------------
    # ➜ On ne demande aucune coordonnée ici
    # ➜ Juste le montant et le statut
    # =====================================================
    commande = Commande(
        total_ttc=total,
        statut='en_attente',
        date_commande=datetime.utcnow()
    )
    db.session.add(commande)
    db.session.commit()

    # Stocker temporairement dans la session Flask
    flask_session['commande_id'] = commande.id

    print(f"🧾 Commande {commande.id} créée (en attente, total {total} €)")

    try:
        # =====================================================
        # 🟢 Étape 2 : Création de la session Stripe
        # =====================================================
        stripe_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Les Silences du Vin"},
                    "unit_amount": montant_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{base_url}/paiement/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/paiement/cancel",
        )

        # =====================================================
        # 🔗 Étape 3 : Lier la commande à la session Stripe
        # =====================================================
        commande.stripe_session_id = stripe_session.id
        db.session.commit()
        print(f"🔗 Commande {commande.id} liée à Stripe {stripe_session.id}")

        # =====================================================
        # 🚀 Étape 4 : Retour JSON pour front ou redirection directe
        # =====================================================
        return jsonify({"id": stripe_session.id})

    except Exception as e:
        current_app.logger.error(f"Erreur Stripe : {type(e).__name__} - {e}")
        flash("Le service de paiement est momentanément indisponible. Veuillez réessayer plus tard.", "warning")
        return redirect(url_for('catalogue.index'))


# ======================================================
# 🟣 3. Webhook Stripe
# ------------------------------------------------------
# ➜ Appelé automatiquement par Stripe
# ➜ Vérifie la signature de sécurité
# ➜ Met à jour la commande en "payé"
# ======================================================
@paiement_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except stripe.error.SignatureVerificationError:
        return "Signature Stripe invalide", 400

    # Événement : paiement validé
    if event['type'] == 'checkout.session.completed':
        session_stripe = event['data']['object']
        commande = Commande.query.filter_by(stripe_session_id=session_stripe['id']).first()
        if commande:
            commande.statut = 'payé'
            db.session.commit()
            print(f"✅ Commande {commande.id} marquée comme payée (via Webhook).")

    return '', 200

# ======================================================
# 🟣 /paiement/infos-livraison
# ------------------------------------------------------
# ➜ Page post-paiement où le client saisit ses coordonnées
# ➜ Met à jour la commande existante après succès Stripe
# ======================================================
@paiement_bp.route('/infos-livraison', methods=['GET', 'POST'])
def infos_livraison():
    commande_id = flask_session.get('commande_id')
    commande = Commande.query.get(commande_id) if commande_id else None

    if not commande:
        flash("Aucune commande à compléter.", "warning")
        return redirect(url_for('catalogue.index'))

    form = GuestCheckoutForm()

    if form.validate_on_submit():
        commande.email_client = form.email.data
        commande.prenom_client = form.prenom.data
        commande.nom_client = form.nom.data
        commande.adresse_livraison = form.adresse_livraison.data
        commande.code_postal_livraison = form.code_postal_livraison.data
        commande.ville_livraison = form.ville_livraison.data
        commande.telephone_livraison = form.telephone.data
        commande.adresse_facturation = form.adresse_facturation.data
        commande.code_postal_facturation = form.code_postal_facturation.data
        commande.ville_facturation = form.ville_facturation.data
        commande.statut = 'complétée'

        db.session.commit()
        flash("Merci ! Vos informations ont bien été enregistrées.", "success")
        flask_session.pop('panier', None)
        return redirect(url_for('catalogue.index'))

    return render_template('paiement/infos_livraison.html', form=form, commande=commande)

# ======================================================
# 🔵 4. Route /success (version post-Stripe)
# ------------------------------------------------------
# ➜ Page de confirmation Stripe
# ➜ Met à jour la commande (statut = payé)
# ➜ Redirige vers /paiement/infos pour compléter les coordonnées
# ======================================================
@paiement_bp.route('/success')
def success():
    session_id = request.args.get('session_id', '')
    if not session_id:
        flash("Session Stripe manquante.", "warning")
        return render_template('paiement/cancel.html')

    # Récupération de la commande liée à cette session Stripe
    commande = Commande.query.filter_by(stripe_session_id=session_id).first()
    if not commande:
        print("⚠️ Aucune commande trouvée pour cette session Stripe.")
        return render_template('paiement/cancel.html')

    # Si la commande n’est pas encore marquée comme payée
    if commande.statut != 'payé':
        commande.statut = 'payé'
        db.session.commit()
        print(f"✅ Commande {commande.id} marquée comme payée.")

    # Stocker l'ID dans la session Flask
    flask_session['commande_id'] = commande.id

    # Rediriger vers la page de saisie des informations client
    return redirect(url_for('paiement.infos_livraison'))


# ======================================================
# 🔴 5. Route /cancel
# ------------------------------------------------------
# ➜ Page affichée si le client annule ou interrompt le paiement Stripe.
# ➜ Ne modifie pas la commande en base (elle reste 'en_attente').
# ======================================================
@paiement_bp.route('/cancel')
def cancel():
    message = (
        "Votre paiement n’a pas été finalisé.<br>"
        "Votre panier reste disponible si vous souhaitez reprendre votre commande."
    )
    return render_template('paiement/cancel.html', message=message)
