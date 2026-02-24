# app/forms/checkout.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class GuestCheckoutForm(FlaskForm):
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=80)])
    nom = StringField('Nom', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])

    adresse_livraison = StringField('Adresse', validators=[DataRequired(), Length(max=255)])
    code_postal_livraison = StringField('Code postal', validators=[DataRequired(), Length(max=20)])
    ville_livraison = StringField('Ville', validators=[DataRequired(), Length(max=80)])
    telephone = StringField('Téléphone (optionnel)', validators=[Length(max=30)])

    same_billing = BooleanField('Adresse de facturation identique')
    adresse_facturation = StringField('Adresse facturation')
    code_postal_facturation = StringField('CP facturation')
    ville_facturation = StringField('Ville facturation')

    submit = SubmitField('Procéder au paiement')
