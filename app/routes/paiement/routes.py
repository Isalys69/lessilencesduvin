import os, stripe
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session as flask_session, redirect, url_for, flash
from flask import current_app
from flask_login import current_user

from app.extensions import db
from app.models.commandes import Commande, CommandeProduit
from app.models.stripe_event import StripeEvent

from app.forms.checkout import GuestCheckoutForm
from app.models.vin import Vin
from app.utils.panier_tools import get_session_panier
from app.utils.email import send_plain_email

from decimal import Decimal
from app.utils.panier_tools import money2, compute_shipping

from sqlalchemy.exc import IntegrityError
from app.extensions import csrf


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

# ======================================================
# 🟢 /paiement/create-checkout-session
# ------------------------------------------------------
# ➜ Crée une commande “en attente” avant le paiement Stripe
# ➜ Lance la session Stripe
# ➜ Associe la commande à la session Stripe (pour suivi du paiement)
# ➜ Redirige ensuite vers Stripe Checkout
# ======================================================

@paiement_bp.route('/create-checkout-session', methods=['POST', 'GET'])
@csrf.exempt
def create_checkout_session():
    panier = get_session_panier()
    if not panier:
        flash("Votre panier est vide.", "warning")
        return redirect(url_for('catalogue.index'))

    # ✅ Base URL (local vs prod)
    if request.host.startswith("127.0.0.1") or "localhost" in request.host:
        base_url = "http://127.0.0.1:5000"
    else:
        base_url = "https://www.lessilencesduvin.fr"

    # ✅ Calcul robustes (mêmes règles que le panier)
    from decimal import Decimal
    from app.utils.panier_tools import money2, compute_shipping

    subtotal = Decimal("0.00")
    for i in panier:
        subtotal += Decimal(str(i["prix"])) * Decimal(str(i["qty"]))
    subtotal = money2(subtotal)

    shipping = money2(compute_shipping(subtotal))
    total_ttc = money2(subtotal + shipping)

    subtotal_cents = int(subtotal * 100)
    shipping_cents = int(shipping * 100)

    # 🧾 Étape 1 : création commande "en attente" avec le TOTAL TTC (produits + livraison)
    commande = Commande(
        total_ttc=float(total_ttc),
        statut='en_attente',
        date_commande=datetime.utcnow()
    )


    db.session.add(commande)
    db.session.commit()

    # 🔒 Étape 1 bis : figer les lignes du panier dans la commande
    for item in panier:
        ligne = CommandeProduit(
            commande_id=commande.id,
            produit_id=item["vin_id"],
            quantite=int(item["qty"]),
            prix_unitaire=float(item["prix"])
        )
        db.session.add(ligne)
    db.session.commit()


    # Stocker temporairement dans la session Flask
    flask_session['commande_id'] = commande.id
    current_app.logger.info(
        f"[CHECKOUT] Commande {commande.id} créée (statut=en_attente, total_ttc={total_ttc} EUR)"
    )

    try:
        # 🟢 Étape 2 : session Stripe (produits + livraison si nécessaire)
        line_items = [
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Vins - Les Silences du Vin"},
                    "unit_amount": subtotal_cents,
                },
                "quantity": 1,
            }
        ]

        if shipping_cents > 0:
            line_items.append({
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": "Livraison (France métropolitaine)"},
                    "unit_amount": shipping_cents,
                },
                "quantity": 1,
            })

        stripe_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=f"{base_url}/paiement/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/paiement/cancel",
            metadata={
                "commande_id": str(commande.id),
                "subtotal_eur": str(subtotal),
                "shipping_eur": str(shipping),
                "total_ttc_eur": str(total_ttc),
            }
        )

        # 🔗 Étape 3 : lier commande ↔ Stripe session
        commande.stripe_session_id = stripe_session.id
        db.session.commit()
        current_app.logger.info(
            f"[CHECKOUT] Commande {commande.id} liée à stripe_session_id={stripe_session.id}"
        )

        # 🚀 Retour JSON pour le front (Stripe redirect)
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
@csrf.exempt
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except stripe.error.SignatureVerificationError:
        return "Signature Stripe invalide", 400
    except Exception as e:
        current_app.logger.error(f"[WEBHOOK] Erreur construct_event: {type(e).__name__} - {e}")
        return "Webhook invalide", 400

    # On ne traite que cet event en V1
    if event.get('type') != 'checkout.session.completed':
        return '', 200

    session_stripe = event['data']['object']

    # --- Stripe IDs ---
    event_id = event.get("id")
    stripe_session_id = session_stripe.get("id")
    payment_intent_id = session_stripe.get("payment_intent")

    if not event_id or not stripe_session_id:
        current_app.logger.error(f"[WEBHOOK] event_id ou stripe_session_id manquant (event_id={event_id}, session_id={stripe_session_id})")
        return '', 200

    # ✅ Barrière #1 : idempotence Stripe par event.id (UNIQUE)
    # Si Stripe rejoue le même event, l'insert échoue -> on retourne 200 immédiatement.
    try:
        db.session.add(StripeEvent(
            event_id=event_id,
            event_type=event.get("type"),
            stripe_session_id=stripe_session_id
        ))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.info(f"[WEBHOOK] Duplicate event ignoré event_id={event_id}")
        return '', 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[WEBHOOK] Erreur insert stripe_events event_id={event_id}: {type(e).__name__} - {e}")
        return '', 200

    # Récupération commande
    commande = Commande.query.filter_by(stripe_session_id=stripe_session_id).first()
    if not commande:
        current_app.logger.error(f"[WEBHOOK] Commande introuvable pour stripe_session_id={stripe_session_id} (event_id={event_id})")
        return '', 200

    # (optionnel mais utile) : relier l'event à la commande pour audit
    try:
        StripeEvent.query.filter_by(event_id=event_id).update({"commande_id": commande.id})
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 🔗 Audit : mémoriser payment_intent sur la commande
    if payment_intent_id and commande.stripe_payment_intent_id != payment_intent_id:
        commande.stripe_payment_intent_id = payment_intent_id
        db.session.commit()

    # ✅ Barrière #2 : garde métier (filet)
    if commande.statut in ('payé', 'complétée', 'echec_stock'):
        current_app.logger.info(f"[WEBHOOK] Commande {commande.id} déjà traitée (statut={commande.statut}) event_id={event_id}")
        return '', 200

    # Helper refund idempotent
    def _safe_refund(commande_obj, payment_intent):
        if not payment_intent:
            return
        if commande_obj.refund_effectue:
            current_app.logger.info(
                f"[WEBHOOK] Refund déjà effectué commande {commande_obj.id} refund_id={commande_obj.stripe_refund_id}"
            )
            return
        try:
            refund = stripe.Refund.create(payment_intent=payment_intent)
            commande_obj.refund_effectue = True
            commande_obj.stripe_refund_id = refund.get("id")
            commande_obj.date_refund = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"[WEBHOOK] Refund OK commande {commande_obj.id} refund_id={commande_obj.stripe_refund_id}")
        except Exception as e:
            current_app.logger.error(f"[WEBHOOK] Refund échoué commande {commande_obj.id}: {type(e).__name__} - {e}")

    # Charger les lignes figées en base
    lignes = CommandeProduit.query.filter_by(commande_id=commande.id).all()
    if not lignes:
        current_app.logger.error(f"[WEBHOOK] Commande {commande.id} sans lignes produits -> echec_stock + refund (event_id={event_id})")
        commande.statut = 'echec_stock'
        db.session.commit()
        _safe_refund(commande, payment_intent_id)
        return '', 200

    # Décrémentation stock atomique ligne à ligne
    from sqlalchemy import update

    try:
        for l in lignes:
            vin_id = int(l.produit_id)
            qty = int(l.quantite)

            stmt = (
                update(Vin)
                .where(Vin.id == vin_id)
                .where(Vin.is_active == True)
                .where(Vin.stock >= qty)
                .values(stock=Vin.stock - qty)
            )
            result = db.session.execute(stmt)
            if result.rowcount != 1:
                raise ValueError(f"Stock insuffisant pour vin_id={vin_id}, qty={qty}")

        # Si tout est OK, on valide stock + statut
        commande.statut = 'payé'
        db.session.commit()
        current_app.logger.info(f"[WEBHOOK] Commande {commande.id} -> payé (stock OK) event_id={event_id}")

        # ✅ Email "Paiement confirmé" (idempotent via flag)
        # Stripe fournit l'email dans customer_details.email (le plus fiable), sinon customer_email.
        stripe_email = None
        try:
            customer_details = session_stripe.get("customer_details") or {}
            stripe_email = customer_details.get("email") or session_stripe.get("customer_email")
        except Exception:
            stripe_email = None

        if stripe_email and not commande.email_paiement_envoye:
            try:
                body = (
                    f"Bonjour,\n\n"
                    f"Votre paiement pour la commande #{commande.id} a bien été confirmé.\n"
                    f"Montant : {commande.total_ttc} €\n\n"
                    f"✅ Dernière étape : merci de renseigner votre adresse de livraison ici :\n"
                    f"https://www.lessilencesduvin.fr/paiement/infos-livraison\n\n"
                    f"Sans ces informations, nous ne pourrons pas expédier votre commande.\n\n"
                    f"Les Silences du Vin"
                )
                
                send_plain_email(
                    subject=f"Paiement confirmé – Commande #{commande.id}",
                    body=body,
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[stripe_email],
                    reply_to="contact@lessilencesduvin.com"
                )
                commande.email_paiement_envoye = True
                commande.date_email_paiement = datetime.utcnow()

                # On en profite pour pré-remplir email_client si vide (utile pour admin)
                if not commande.email_client:
                    commande.email_client = stripe_email

                db.session.commit()
                current_app.logger.info(f"[WEBHOOK] Email paiement envoyé commande {commande.id} -> {stripe_email}")
            except Exception as e:
                current_app.logger.error(f"[WEBHOOK] Erreur envoi email paiement commande {commande.id}: {type(e).__name__} - {e}")
        else:
            if not stripe_email:
                current_app.logger.warning(f"[WEBHOOK] Email Stripe absent, email paiement non envoyé commande {commande.id}")
            elif commande.email_paiement_envoye:
                current_app.logger.info(f"[WEBHOOK] Email paiement déjà envoyé commande {commande.id}")




        return '', 200

    except Exception as e:
        db.session.rollback()

        current_app.logger.warning(f"[WEBHOOK] Commande {commande.id} -> echec_stock ({type(e).__name__}: {e}) event_id={event_id}")
        commande.statut = 'echec_stock'
        db.session.commit()

        _safe_refund(commande, payment_intent_id)

        # Option : email justificatif si email déjà connu
        if commande.email_client:
            try:
                body = (
                    f"Bonjour,\n\n"
                    f"Votre commande #{commande.id} a été remboursée automatiquement.\n"
                    f"Motif : le vin a été vendu simultanément et le stock n'était plus suffisant.\n\n"
                    f"Le remboursement a été initié immédiatement. Selon votre banque, il peut apparaître sous quelques jours.\n\n"
                    f"Les Silences du Vin"
                )
                send_plain_email(
                    subject="Remboursement automatique – rupture de stock",
                    body=body,
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[commande.email_client],
                    reply_to="contact@lessilencesduvin.com"
                )
            except Exception as me:
                current_app.logger.error(f"[WEBHOOK] Erreur email remboursement commande {commande.id}: {type(me).__name__} - {me}")

        return '', 200
# ======================================================
# 🟣 /paiement/infos-livraison
# ------------------------------------------------------
# ➜ Page post-paiement où le client saisit ses coordonnées
# ➜ Met à jour la commande existante après succès Stripe
# ➜ Envoie un courriel de confirmation au client
# ======================================================
@paiement_bp.route('/infos-livraison', methods=['GET', 'POST'])
def infos_livraison():
    from sqlalchemy import update
    from datetime import datetime

    commande_id = flask_session.get('commande_id')
    commande = Commande.query.get(commande_id) if commande_id else None

    if not commande:
        flash("Aucune commande à compléter.", "warning")
        return redirect(url_for('catalogue.index'))

    # ✅ Idempotence UX
    if commande.statut == "complétée":
        return redirect(url_for("catalogue.index"))

    # ✅ Garde stricte paiement (barrière métier)
    if commande.statut != "payé":
        flash("Cette commande n'est pas confirmée comme payée.", "warning")
        return redirect(url_for("catalogue.index"))

    form = GuestCheckoutForm()

    if form.validate_on_submit():
        now = datetime.utcnow()

        # ✅ Transition atomique payé -> complétée + verrou email (anti double POST / anti double email)
        stmt = (
            update(Commande)
            .where(Commande.id == commande.id)
            .where(Commande.statut == "payé")
            .where(Commande.email_completion_envoye == False)
            .values(
                email_client=form.email.data,
                prenom_client=form.prenom.data,
                nom_client=form.nom.data,
                adresse_livraison=form.adresse_livraison.data,
                code_postal_livraison=form.code_postal_livraison.data,
                ville_livraison=form.ville_livraison.data,
                telephone_livraison=form.telephone.data,
                adresse_facturation=form.adresse_facturation.data,
                code_postal_facturation=form.code_postal_facturation.data,
                ville_facturation=form.ville_facturation.data,
                statut="complétée",
                email_completion_envoye=True,
                date_email_completion=now,
            )
        )

        try:
            result = db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"[INFOS] Erreur DB complétion commande {commande.id}: {type(e).__name__} - {e}"
            )
            flash("Une erreur est survenue. Veuillez réessayer.", "warning")
            return redirect(url_for("paiement.infos_livraison"))

        if result.rowcount != 1:
            # Déjà complétée OU pas payée OU déjà email envoyé -> aucun envoi
            current_app.logger.info(
                f"[INFOS] Complétion ignorée (rowcount=0) commande_id={commande.id} "
                f"statut_actuel={commande.statut} email_completion_envoye={commande.email_completion_envoye}"
            )
            flash("Cette commande a déjà été traitée ou n'est pas éligible.", "warning")
            return redirect(url_for("catalogue.index"))

        # ✅ Email "Informations reçues" (exactly-once grâce au verrou DB ci-dessus)
        try:
            body = (
                f"Bonjour {form.prenom.data},\n\n"
                f"Nous avons bien reçu vos informations de livraison pour la commande #{commande.id}.\n"
                f"Montant : {commande.total_ttc} €\n\n"
                f"Adresse de livraison :\n"
                f"{form.adresse_livraison.data}\n"
                f"{form.code_postal_livraison.data} {form.ville_livraison.data}\n\n"
                f"Les Silences du Vin"
            )
            send_plain_email(
                subject=f"Informations reçues – Commande #{commande.id}",
                body=body,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[form.email.data],
                reply_to="contact@lessilencesduvin.com"
            )
            current_app.logger.info(f"[INFOS] Email complétion envoyé commande {commande.id} -> {form.email.data}")
        except Exception as e:
            # V1: on ne "déverrouille" pas le flag, sinon risque de doubles envois.
            current_app.logger.error(
                f"[INFOS] Erreur envoi email complétion commande {commande.id}: {type(e).__name__} - {e}"
            )

        flash("Merci ! Vos informations ont bien été enregistrées.", "success")

        # Nettoyage session
        flask_session.pop('panier', None)
        flask_session.pop('commande_id', None)

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
        current_app.logger.warning(
            f"[SUCCESS] Aucune commande trouvée pour stripe_session_id={session_id}"
        )
        return render_template('paiement/cancel.html')

    # ✅ /success ne décide pas du statut: le webhook est l'autorité
    if commande.statut == 'echec_stock':
        flash("Désolé, le stock n'était plus disponible. Votre paiement a été remboursé automatiquement.", "warning")
        return render_template('paiement/cancel.html')

    if commande.statut != 'payé':
        # webhook pas encore passé (délai), ou commande encore en_attente
        flash("Votre paiement est en cours de confirmation. Veuillez patienter quelques secondes et rafraîchir la page.", "warning")
        return render_template('paiement/cancel.html')

    # Stocker l'ID dans la session Flask
    flask_session['commande_id'] = commande.id

    # ✅ Info délivrabilité : message à l'écran (utile même si le mail tombe en indésirables)
    flash(
        "Un email de confirmation vient de vous être envoyé. "
        "Si vous ne le voyez pas, pensez à vérifier votre dossier courrier indésirable / spam.",
        "info"
    )

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
