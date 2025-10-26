from flask import Blueprint, render_template, Response
from app.utils.panier_tools import get_compteur_panier

TEMPLATE_ACCUEIL = "construction.html"  # deviendra "accueil.html" plus tard

# Création du Blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    compteur = get_compteur_panier()
    return render_template(TEMPLATE_ACCUEIL, compteur=compteur)


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
