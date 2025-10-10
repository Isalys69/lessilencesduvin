import os
from dotenv import load_dotenv

# ✅ Assure le chargement du .env s’il existe
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clé_par_défaut')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'ssl0.ovh.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True') == 'True'

    # ✅ Protection : évite le .split sur None
    raw_recipients = os.getenv('MAIL_RECIPIENT', '')
    MAIL_RECIPIENT = [r.strip() for r in raw_recipients.split(',') if r.strip()]
