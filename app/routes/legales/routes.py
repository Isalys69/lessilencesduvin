from flask import Blueprint, render_template

legales_bp = Blueprint('legales', __name__, url_prefix='/legales')

@legales_bp.route('/mentions')
def mentions():
    return render_template('legales/mentions.html')

@legales_bp.route('/cgv')
def cgv():
    return render_template('legales/cgv.html')

@legales_bp.route('/confidentialite')
def confidentialite():
    return render_template('legales/confidentialite.html')
