from django.apps import AppConfig
from django.db.models.signals import post_save


class ThreatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.threat'
    label = 'threat'

    def ready(self):
        from .signals import create_hazard

        post_save.connect(
            create_hazard,
            sender=self.get_model('Hazard'),
            dispatch_uid='create_hazard'
        )
