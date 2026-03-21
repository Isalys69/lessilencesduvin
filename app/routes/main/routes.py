from flask import Blueprint, render_template, Response, request, flash, redirect, url_for
from app.utils.panier_tools import get_compteur_panier
from app.models.vin import Vin

# Création du Blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    compteur = get_compteur_panier()
    vin_vedette = (
        Vin.query
        .filter(Vin.is_active == True, Vin.stock > 0)
        .order_by(Vin.prix.desc())
        .first()
    )
    return render_template('accueil.html', compteur=compteur, vin_vedette=vin_vedette)

@main_bp.route('/newsletter', methods=['POST'])
def newsletter():
    # V1 : enregistrement à implémenter — on confirme la réception
    flash("Merci ! Vous serez parmi les premiers informés des prochaines arrivées.", "success")
    return redirect(url_for('main.index'))


# ---------------------------
# 🔒 Robots.txt
# ---------------------------
@main_bp.route('/robots.txt')
def robots():
    content = """User-agent: *
Disallow: /admin/
Allow: /static/
Allow: /

Sitemap: https://www.lessilencesduvin.fr/sitemap.xml
"""
    return Response(content, mimetype='text/plain')


# ---------------------------
# 🗺️ Sitemap.xml
# ---------------------------
@main_bp.route('/sitemap.xml')
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.lessilencesduvin.fr/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.lessilencesduvin.fr/catalogue</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.lessilencesduvin.fr/contact</loc>
    <priority>0.6</priority>
  </url>
</urlset>"""
    return Response(xml, mimetype='application/xml')
