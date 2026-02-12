from flask import Blueprint, render_template, abort
from sqlalchemy.orm import joinedload
from app.models.vin import Vin

vins_bp = Blueprint('vins', __name__)

@vins_bp.route('/vins/<couleur>')
def afficher_vins(couleur):
    couleur_norm = couleur.strip().lower()

    if couleur_norm == "garde":
        vins = (
            Vin.query
            .options(joinedload(Vin.domaine))
            .filter(Vin.is_active.is_(True))
            .order_by(Vin.nom.asc())
            .all()
        )
        libelle = "Garde"
    else:
        vins = (
            Vin.query
            .options(joinedload(Vin.domaine))
            .filter(Vin.is_active.is_(True))
            .filter(Vin.couleur.ilike(couleur_norm))
            .order_by(Vin.nom.asc())
            .all()
        )
        libelle = couleur_norm.capitalize() + "s" if couleur_norm != "rose" else "Rosés"

    textes_intro = {
        'Rouges': "Découvrez notre sélection de vins rouges, profonds et vibrants.",
        'Blancs': "Découvrez nos vins blancs, lumineux et précis.",
        'Rosés': "Découvrez nos vins rosés, frais et délicats.",
        'Garde': "Découvrez nos vins de garde, patinés par le temps et la mémoire.",
        'Orange': "Découvrez nos vins orange, singuliers et texturés.",
    }
    texte_intro = textes_intro.get(libelle, f"Découvrez nos vins {libelle.lower()}, choisis pour leur sincérité.")

    return render_template(
        'vins_couleur.html',
        vins=vins,
        couleur=libelle,
        texte_intro=texte_intro
    )

# Fiche vin (détail)
@vins_bp.route('/vin/<int:vin_id>')
def vin_detail(vin_id):
    vin = (
        Vin.query
        .options(joinedload(Vin.domaine))
        .filter(Vin.is_active.is_(True))
        .filter(Vin.id == vin_id)
        .first()
    )
    
    if not vin:
        abort(404)
    return render_template('vin_detail.html', vin=vin)
