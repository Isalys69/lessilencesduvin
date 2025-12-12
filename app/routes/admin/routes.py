from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.vin import Vin
from app.models.domaine import Domaine
from app.models.commandes import Commande

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/add-wine", methods=["GET", "POST"])
@login_required
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
def commandes():
    commandes = (
        Commande.query.order_by(Commande.date_commande.desc()).all()
        if hasattr(Commande, "query")
        else []
    )
    return render_templa_
