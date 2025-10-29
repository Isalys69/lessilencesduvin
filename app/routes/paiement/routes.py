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
# 🟢 1. Route /checkout
# ------------------------------------------------------
# ➜ Affiche le formulaire de coordonnées postales
# ➜ Crée une commande "en_attente" dans la base
# ➜ Stocke l'id de la commande dans la session Flask
# ➜ Redirige vers Stripe Checkout
# ======================================================
@paiement_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = GuestCheckoutForm()
    panier = get_session_panier()
    total = sum(i['prix'] * i['qty'] for i in panier)

    if not panier:
        flash("Votre panier est vide.", "warning")
        return redirect(url_for('catalogue.catalogue'))

    # Si le formulaire est validé, création d'une commande
    if form.validate_on_submit():
        commande = Commande(
            user_id=current_user.user_id if current_user.is_authenticated else None,
            email_client=form.email.data,
            prenom_client=form.prenom.data,
            nom_client=form.nom.data,
            adresse_livraison=form.adresse_livraison.data,
            code_postal_livraison=form.code_postal_livraison.data,
            ville_livraison=form.ville_livraison.data,
            telephone_livraison=form.telephone.data,
            total_ttc=total,
            statut='en_attente',
            date_commande=datetime.utcnow()
        )
        db.session.add(commande)
        db.session.commit()

        # Stocker l'id de la commande pour la lier ensuite à Stripe
        flask_session['commande_id'] = commande.id

        print(f"🧾 Commande {commande.id} créée (en attente, total {total} €)")

        # Redirection vers la création de la session Stripe
        return redirect(url_for('paiement.create_checkout_session'))

    # En GET : afficher le formulaire de coordonnées
    return render_template('checkout.html', form=form, panier=panier, total=total)


# ======================================================
# 🟠 2. Route /create-checkout-session
# ------------------------------------------------------
# ➜ Crée la session Stripe pour le paiement réel.
# ➜ Lie la session Stripe à la commande déjà créée (statut "en_attente").
# ➜ En cas d’impossibilité d’accès à l’API Stripe (proxy, réseau, etc.),
#     un mode simulation est automatiquement déclenché :
#       - une session fictive TEST_SESSION_xxx est créée,
#       - la commande est liée à cette session simulée,
#       - l’utilisateur est redirigé directement vers /success.
# ======================================================
@paiement_bp.route('/create-checkout-session', methods=['POST', 'GET'])
def create_checkout_session():
    panier = get_session_panier()
    total = sum(i['prix'] * i['qty'] for i in panier)
    montant_cents = int(float(total) * 100)

    # Détection environnement : local ou production
    if request.host.startswith("127.0.0.1") or "localhost" in request.host:
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = "https://www.lessilencesduvin.fr"

    # Récupération de la commande en attente
    commande_id = flask_session.get("commande_id")
    commande = Commande.query.get(commande_id) if commande_id else None

    try:
        # =====================================================
        # ✅ Tentative de création de session Stripe réelle
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

        # Lier la session Stripe à la commande
        if commande:
            commande.stripe_session_id = stripe_session.id
            db.session.commit()
            print(f"🔗 Commande {commande.id} liée à Stripe {stripe_session.id}")

        # Retour JSON pour intégration front
        return jsonify({"id": stripe_session.id})

    except Exception as e:
        current_app.logger.error(f"Erreur Stripe : {type(e).__name__} - {e}")
        flash("Le service de paiement est momentanément indisponible. Veuillez réessayer plus tard.", "warning")
        return redirect(url_for('paiement.checkout'))

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
# 🔵 4. Route /success
# ------------------------------------------------------
# ➜ Page de confirmation après paiement
# ➜ Vérifie la commande, met à jour le statut si besoin
# ➜ Vide le panier
# ======================================================
@paiement_bp.route('/success')
def success():
    session_id = request.args.get('session_id', '')
    if not session_id:
        flash("Session Stripe manquante", "warning")
        return render_template('paiement/cancel.html')

    # Récupération de la commande liée à cette session Stripe
    commande = Commande.query.filter_by(stripe_session_id=session_id).first()
    if not commande:
        print("⚠️ Aucune commande trouvée pour cette session Stripe.")
        return render_template('paiement/cancel.html')

    # Si le webhook n'a pas encore confirmé, on le fait ici
    if commande.statut != 'payé':
        commande.statut = 'payé'
        db.session.commit()

    print(f"Commande {commande.id} validée ✅")

    # Nettoyage de la session Flask
    flask_session.pop('panier', None)
    flask_session.pop('commande_id', None)

    # Afficher la page de succès
    return render_template('paiement/success.html', commande=commande)


# ======================================================
# 🔴 5. Route /cancel
# ------------------------------------------------------
# ➜ Page affichée si le client annule ou interrompt le paiement Stripe.
# ➜ Récupère le panier actuel en session pour maintenir l’affichage du badge
#     "Panier (n)" dans base.html.
# ➜ Ne modifie pas la commande en base (elle reste 'en_attente').
# ======================================================
@paiement_bp.route('/cancel')
def cancel():
    panier = get_session_panier()
    panier_count = sum(i['qty'] for i in panier)
    return render_template('paiement/cancel.html', panier_count=panier_count)
