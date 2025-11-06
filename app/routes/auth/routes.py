from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.models.user import User
from app.forms.auth_form import RegistrationForm, LoginForm
from app import db


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Un compte existe déjà avec cet e-mail.", "warning")
            return redirect(url_for('auth.register'))

        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            db.session.permanent = True
            flash("Connexion réussie !", "success")

            # Vérifie le paramètre 'next' envoyé par Flask-Login
            next_page = request.args.get('next')

            # Empêche de revenir sur une route non-GET (comme /save_cart)
            if next_page and next_page.startswith('/panier/save_cart'):
                next_page = url_for('panier.index')

            # Redirige proprement
            return redirect(next_page or url_for('main.index'))

        flash("Identifiants invalides. Vérifiez votre e-mail ou mot de passe.", "danger")

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('main.index'))
