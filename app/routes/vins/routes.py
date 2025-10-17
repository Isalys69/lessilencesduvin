from flask import Blueprint, render_template
from app.data import get_vins_par_couleur

vins_bp = Blueprint('vins', __name__)

@vins_bp.route('/vins/<couleur>')
def afficher_vins(couleur):
    vins = get_vins_par_couleur(couleur)

    textes_intro = {
        'Rouges': "Découvrez notre sélection de vins rouges, profonds et vibrants.",
        'Blancs': "Découvrez nos vins blancs, lumineux et précis.",
        'Rosés': "Découvrez nos vins rosés, frais et délicats.",
        'Garde': "Découvrez nos vins de garde, patinés par le temps et la mémoire.",
        'Pétillants': "Découvrez nos vins pétillants, festifs et raffinés.",
    }
    texte_intro = textes_intro.get(couleur, f"Découvrez nos vins {couleur.lower()}, choisis pour leur sincérité.")

    return render_template(
        'vins_couleur.html',
        vins=vins,
        couleur=couleur,
        texte_intro=texte_intro
    )
