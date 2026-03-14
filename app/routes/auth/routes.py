from flask import Blueprint, current_app
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.models.user import User
from app.forms.auth_form import RegistrationForm, LoginForm
from app.extensions import db
from app.utils.email import send_plain_email
from app.extensions import csrf


def _generate_reset_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset')


def _verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return email


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

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@csrf.exempt
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()

        # Réponse identique que l'email existe ou non (anti-énumération)
        if user:
            token = _generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            try:
                send_plain_email(
                    subject="Réinitialisation de votre mot de passe – Les Silences du Vin",
                    body=(
                        f"Bonjour,\n\n"
                        f"Vous avez demandé à réinitialiser votre mot de passe.\n"
                        f"Cliquez sur le lien ci-dessous (valable 1 heure) :\n\n"
                        f"{reset_url}\n\n"
                        f"Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail.\n\n"
                        f"Les Silences du Vin"
                    ),
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[user.email],
                    reply_to="contact@lessilencesduvin.com"
                )
            except Exception as e:
                current_app.logger.error(f"[RESET] Erreur envoi email {user.email}: {e}")

        flash("Si un compte existe avec cet e-mail, un lien de réinitialisation vient d'être envoyé.", "info")
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@csrf.exempt
def reset_password(token):
    email = _verify_reset_token(token)
    if not email:
        flash("Ce lien est invalide ou a expiré.", "danger")
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if len(password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
        elif password != confirm:
            flash("Les mots de passe ne correspondent pas.", "danger")
        else:
            user.set_password(password)
            db.session.commit()
            flash("Mot de passe mis à jour. Vous pouvez vous connecter.", "success")
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie.", "info")
    return redirect(url_for('main.index'))
