from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ParserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'krisha_parser.parser'
    verbose_name = _("Parser")
