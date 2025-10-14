from flask import Blueprint, render_template, request, jsonify,redirect,url_for
from app.data.panier_data import PANIER  
from app.utils.panier_tools import get_compteur_panier

panier_bp = Blueprint('panier', __name__, url_prefix='/panier')


# 🔹 Fonction utilitaire interne (un seul rendu du panier)
def render_panier():
    items = [
        {
            'vin_id': i['vin_id'],
            'nom': i['nom'],
            'prix': i['prix'],
            'qty': i['qty'],
            'line_total': i['prix'] * i['qty']
        }
        for i in PANIER
    ]
    total = sum(i['line_total'] for i in items)
    compteur = get_compteur_panier()

    return render_template('shoppingbasket.html', items=items, total=total, compteur=compteur)



@panier_bp.route('/')
def index():
    return render_panier()

@panier_bp.route('/ajouter', methods=['POST'])
def ajouter():
    data = request.get_json()
    vin_id = str(data.get('vin_id'))
    nom = data.get('nom')
    prix = float(data.get('prix', 0))

    # 🔹 vérifie si le vin existe déjà
    for item in PANIER:
        if item['vin_id'] == vin_id:
            item['qty'] += 1
            break
    else:
        PANIER.append({'vin_id': vin_id, 'nom': nom, 'prix': prix, 'qty': 1})

    # ✅ Calcule le total de bouteilles dans le panier
    total_qty = sum(item['qty'] for item in PANIER)

    return jsonify({
        'message': f'{nom} ajouté',
        'panier': PANIER,
        'total_qty': total_qty
    }), 200


@panier_bp.route('/update_cart', methods=['POST'])
def update_cart():
    vin_id = request.form.get('vin_id')
    action = request.form.get('action')

    for item in PANIER:
        if str(item['vin_id']) == str(vin_id):
            if action == 'increase':
                item['qty'] += 1
            elif action == 'decrease' and item['qty'] > 1:
                item['qty'] -= 1
            elif action == 'remove':
                PANIER.remove(item)
            break

    return render_panier()


@panier_bp.route('/checkout', methods=['POST'])
def checkout():
    # pour la V1, on "simule" juste la sauvegarde
    print("Panier sauvegardé :", PANIER)
    return redirect(url_for('panier.index'))
