from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.vin import Vin
from app.models.domaine import Domaine
from app.models.commandes import Commande
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/add-wine', methods=['GET', 'POST'])
# @login_required  # à activer plus tard si besoin
def add_wine():

    if request.method == 'POST':
        vin = Vin(
            nom=request.form['nom'],
            domaine_id=request.form['domaine_id'],
            annee=request.form.get('annee'),
            couleur=request.form['couleur'],
            prix=float(request.form['prix']),
            stock=int(request.form['stock']),
            photo=request.form.get('photo')
        )
        db.session.add(vin)
        db.session.commit()
        flash("Vin ajouté.", "success")
        return redirect(url_for('admin.add_wine'))

    domaines = Domaine.query.all()
    return render_template("admin/add_wine.html", domaines=domaines)


@admin_bp.route("/commandes", methods=['GET'])
# @login_required  # optionnel en V1
def commandes():
    commandes = (
        Commande.query
        .order_by(Commande.id.desc())
        .limit(50)
        .all()
    )
    return render_template("admin/commandes.html", commandes=commandes)
