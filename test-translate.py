from flask_babel import support
cat = support.Translations.load('translations', ['it'])
print(cat.gettext("Accéder à la cave"))
