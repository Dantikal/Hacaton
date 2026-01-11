from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TeamsConfig(AppConfig):
    default_auto_field = 'id'
    name = 'teams'
    verbose_name = _('Teams')
