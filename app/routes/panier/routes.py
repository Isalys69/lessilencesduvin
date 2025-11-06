import os
import json
from flask import Blueprint, render_template, request, jsonify,redirect,url_for, flash
from app.utils.panier_tools import get_session_panier, set_session_panier, get_compteur_panier
from flask_login import current_user, login_required
from app.models.panier_sauvegarde import PanierSauvegarde
from app import db

panier_bp = Blueprint('panier', __name__, url_prefix='/panier')





# 🔹 Fonction utilitaire interne (un seul rendu du panier)
def render_panier():

    stripe_public_key = os.getenv("STRIPE_PUBLIC_KEY")

    panier=get_session_panier()
    items = [
        {
            'vin_id': i['vin_id'],
            'nom': i['nom'],
            'prix': i['prix'],
            'qty': i['qty'],
            'line_total': i['prix'] * i['qty']
        }
        for i in panier
    ]
    total = sum(i['line_total'] for i in items)
    compteur = get_compteur_panier()



    return render_template('shoppingbasket.html', items=items, total=total, compteur=compteur, stripe_public_key=stripe_public_key)



@panier_bp.route('/')
def index():
    return render_panier()

@panier_bp.route('/ajouter', methods=['POST'])
def ajouter():
    panier=get_session_panier()
    data = request.get_json()
    vin_id = str(data.get('vin_id'))
    nom = data.get('nom')
    prix = float(data.get('prix', 0))

    # 🔹 vérifie si le vin existe déjà
    for item in panier:
        if item['vin_id'] == vin_id:
            item['qty'] += 1
            break
    else:
        panier.append({'vin_id': vin_id, 'nom': nom, 'prix': prix, 'qty': 1})

    # ✅ Sauuvegarde le panier mis à jour dans la session
    set_session_panier(panier)

    # ✅ Calcule le total de bouteilles dans le panier
    total_qty = sum(item['qty'] for item in panier)

    return jsonify({
        'message': f'{nom} ajouté',
        'panier': panier,
        'total_qty': total_qty
    }), 200


@panier_bp.route('/update_cart', methods=['POST'])
def update_cart():
    panier=get_session_panier()
    vin_id = request.form.get('vin_id')
    action = request.form.get('action')

    for item in panier:
        if str(item['vin_id']) == str(vin_id):
            if action == 'increase':
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
@login_required
def save_cart():
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
