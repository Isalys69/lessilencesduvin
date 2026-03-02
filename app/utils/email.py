import ssl
import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_plain_email(subject, body, sender, recipients, reply_to=None):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["Bcc"] = "contact@lessilencesduvin.fr"


    current_app.logger.info(
        f"[MAIL] subject={msg['Subject']} to={msg.get('To')} bcc={msg.get('Bcc')} from={msg.get('From')}"
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        current_app.config['MAIL_SERVER'],
        current_app.config['MAIL_PORT'],
        context=context
    ) as server:
        server.login(
            current_app.config['MAIL_USERNAME'],
            current_app.config['MAIL_PASSWORD']
        )


        try:
            server.send_message(msg)
        except Exception as e:
            current_app.logger.error(f"[MAIL] send failed: {type(e).__name__} - {e}")
            raise
        