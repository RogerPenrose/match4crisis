""" 
Europe Country Codes -> see https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Country_codes/de
"""


from django.utils.translation import gettext_lazy as _


countries=(
    ("", _("Land wählen")), # Empty label for dropdown selects
    ("DE", _("Deutschland")),
    ("PL", _("Polen")),
    ("AT", _("Österreich")),
    # TODO add more as necessary
)