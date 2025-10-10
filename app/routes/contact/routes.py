
import smtplib, ssl
from email.mime.text import MIMEText
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from app.forms.contact_form import ContactForm

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')

@contact_bp.route('/', methods=['GET', 'POST'])
def index():
    form = ContactForm()
    if form.validate_on_submit():
        msg = MIMEText(
            f"Nom : {form.nom.data}\n"
            f"Email : {form.email.data}\n\n"
            f"{form.message.data}",
            "plain", "utf-8"
        )
        msg["Subject"] = "Message via Les Silences du Vin"
        msg["From"] = form.email.data
        msg["To"] = current_app.config['MAIL_RECIPIENT']

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT'],
                context=context
            ) as server:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
                server.send_message(msg)
            flash("Votre message a bien été envoyé. Merci pour votre confiance.", "success")
        except Exception as e:
            current_app.logger.error(f"Erreur d’envoi : {e}")
            flash("Une erreur est survenue. Merci de réessayer plus tard.", "danger")

        return redirect(url_for('contact.index'))

    return render_template('contact.html', form=form)
