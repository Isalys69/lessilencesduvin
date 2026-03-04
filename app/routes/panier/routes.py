import os
import json
from flask import Blueprint, render_template, request, jsonify,redirect,url_for, flash
from flask_login import current_user, login_required
from app.models.panier_sauvegarde import PanierSauvegarde
from app.models.vin import Vin
from app import db
from decimal import Decimal
from app.extensions import csrf
from app.utils.panier_tools import (
    get_session_panier,
    set_session_panier,
    get_compteur_panier,
    compute_shipping,
    money2,
    FREE_SHIPPING_THRESHOLD
)


panier_bp = Blueprint('panier', __name__, url_prefix='/panier')





# 🔹 Fonction utilitaire interne (un seul rendu du panier)
def render_panier():
    stripe_public_key = os.getenv("STRIPE_PUBLIC_KEY")

    panier = get_session_panier()
    items = [
        {
            'vin_id': i['vin_id'],
            'nom': i['nom'],
            'prix': float(i['prix']),  # on garde float pour l'affichage ligne si tu veux
            'qty': i['qty'],
            'line_total': float(i['prix']) * i['qty']
        }
        for i in panier
    ]

    # ✅ Totaux en Decimal (fiables)
    subtotal = sum((Decimal(str(i['prix'])) * Decimal(str(i['qty']))) for i in panier) if panier else Decimal("0.00")
    subtotal = money2(subtotal)

    shipping = compute_shipping(subtotal)
    shipping = money2(shipping)

    total_ttc = money2(subtotal + shipping)

    compteur = get_compteur_panier()

    return render_template(
        'shoppingbasket.html',
        items=items,
        subtotal=float(subtotal),
        shipping=float(shipping),
        total_ttc=float(total_ttc),
        free_shipping_threshold=float(FREE_SHIPPING_THRESHOLD),
        compteur=compteur,
        stripe_public_key=stripe_public_key
    )

@panier_bp.route('/')
def index():
    return render_panier()


@panier_bp.route('/ajouter', methods=['POST'])
@csrf.exempt
def ajouter():
    panier = get_session_panier()
    data = request.get_json(silent=True) or {}

    vin_id = int(data.get("vin_id"))

    vin = Vin.query.get(vin_id)
    if not vin:
        return jsonify({"error": "Vin introuvable"}), 404


    # 🔒 Blocage V1 : impossible de dépasser le stock réel
    if vin.stock <= 0:
        return jsonify({
            "error": "stock_insuffisant",
            "message": "Ce vin est en rupture.",
            "stock_dispo": int(vin.stock),
            "qty_actuelle": 0
        }), 409

    qty_actuelle = 0
    for it in panier:
        if int(it.get("vin_id")) == vin_id:
            qty_actuelle = int(it.get("qty", 0))
            break

    if qty_actuelle + 1 > int(vin.stock):
        flash(f"Stock limité : {vin.stock} bouteille(s) disponible(s).", "warning")
        return jsonify({"error": "stock_insuffisant"}), 409


    nom = vin.nom
    prix = float(vin.prix)

    # Comparaison en int
    for item in panier:
        if int(item["vin_id"]) == vin_id:
            item["qty"] += 1
            break
    else:
        panier.append({
            "vin_id": vin_id,  # stocké en int
            "nom": nom,
            "prix": prix,
            "qty": 1
        })

    set_session_panier(panier)

    total_qty = sum(int(item.get('qty', 0)) for item in panier)

    return jsonify({
        "message": f"{nom} ajouté",
        "total_qty": total_qty
    }), 200


@panier_bp.route('/update_cart', methods=['POST'])
@csrf.exempt
@login_required
def update_cart():
    panier=get_session_panier()
    vin_id = request.form.get('vin_id')
    action = request.form.get('action')

    for item in panier:
        if str(item['vin_id']) == str(vin_id):

            if action == 'increase':
                vin = Vin.query.get(int(item["vin_id"]))
                if not vin or not vin.is_active:
                    flash("Ce vin n'est plus disponible.", "warning")
                elif int(item['qty']) + 1 > int(vin.stock):
                    flash(f"Stock limité : {vin.stock} bouteille(s) disponible(s).", "warning")
                else:
                    item['qty'] += 1

            elif action == 'decrease':
                item['qty'] -= 1
            elif action == 'remove':
                panier.remove(item)
            break

    # 🔹 Supprime les vins dont la quantité est tombée à 0 ou moins
    panier = [i for i in panier if i['qty'] > 0]

    # ✅ Sauvegarde le panier mis à jour dans la session
    set_session_panier(panier)    

    return render_panier()

@panier_bp.route('/compteur', methods=['GET'])
def compteur():
    """
    Retourne en JSON le nombre total d'articles dans le panier de la session.
    Sert aux mises à jour dynamiques du compteur (AJAX / fetch JS).
    """
    total = get_compteur_panier()
    return jsonify({'compteur': total})

from flask import flash, redirect, url_for, jsonify, request

@panier_bp.route('/save_cart', methods=['POST'])
@csrf.exempt
@login_required
def save_cart():
    if not current_user.is_authenticated:
        flash("Connectez-vous pour enregistrer votre panier 💾", "warning")
        return redirect(url_for('auth.login', next=url_for('panier.index')))    

    panier = get_session_panier()
    if not panier:
        flash("Votre panier est vide, rien à enregistrer.", "warning")
        return redirect(url_for('panier.index'))

    data = json.dumps(panier, ensure_ascii=False)
    existant = PanierSauvegarde.query.filter_by(
        user_id=current_user.user_id,
        contenu_json=data
    ).first()

    if existant:
        flash("💾 Ce panier est déjà sauvegardé.", "info")
    else:
        sauvegarde = PanierSauvegarde(user_id=current_user.user_id, contenu_json=data)
        db.session.add(sauvegarde)
        db.session.commit()
        flash("✅ Votre panier a été sauvegardé avec succès.", "success")

    return redirect(url_for('panier.index'))
