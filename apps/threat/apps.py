from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save


class ThreatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.threat'
    label = 'threat'

    def ready(self):
        from .signals import pre_create_hazard, post_create_hazard

        pre_save.connect(
            pre_create_hazard,
            sender=self.get_model('Hazard'),
            dispatch_uid='pre_create_hazard'
        )

        post_save.connect(
            post_create_hazard,
            sender=self.get_model('Hazard'),
            dispatch_uid='post_create_hazard'
        )
