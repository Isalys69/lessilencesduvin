# app/translations.py

TRANSLATIONS = {
    "fr": {
        "html_lang": "fr",
        "agegate_title": "Accès réservé – Les Silences du Vin",
        "slogan": "Il y a des silences qui ne se partagent qu’avec le temps.",
        "access_condition": "Ce lieu s’adresse à celles et ceux qui ont déjà franchi le seuil des 18 ans.",
        "birthdate_label": "Merci d’indiquer votre date de naissance.",
        "btn_access": "Accéder à la cave",
        "abuse_warning": "L’abus d’alcool est dangereux pour la santé.",
        "minors_warning": "Vente interdite aux mineurs.",
        "error_minor": "Accès interdit aux mineurs.",
        "error_invalid": "Date de naissance invalide."
    },
    "it": {
        "html_lang": "it",
        "agegate_title": "Accesso riservato – Les Silences du Vin",
        "slogan": "Ci sono silenzi che si condividono solo con il tempo.",
        "access_condition": "Questo luogo è riservato a chi ha già superato la soglia dei 18 anni.",
        "birthdate_label": "Indica la tua data di nascita, per favore.",
        "btn_access": "Accedi alla cantina",
        "abuse_warning": "L'abuso di alcol è pericoloso per la salute.",
        "minors_warning": "Vendita vietata ai minori.",
        "error_minor": "Accesso vietato ai minori.",
        "error_invalid": "Data di nascita non valida."
    }
}

def get_translations(lang):
    """Retourne le sous-dictionnaire de traduction pour la langue demandée, fallback français."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"])
