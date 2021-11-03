from django.apps import AppConfig
from django.db.models.signals import post_save


class GenericConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.generic'
    label = 'generic'

    def ready(self):
        from .signals import create_comment, create_confirmation, create_reaction

        post_save.connect(
            create_comment,
            sender=self.get_model('Comment'),
            dispatch_uid='create_comment'
        )

        post_save.connect(
            create_confirmation,
            sender=self.get_model('Confirmation'),
            dispatch_uid='create_confirmation'
        )

        post_save.connect(
            create_reaction,
            sender=self.get_model('Reaction'),
            dispatch_uid='create_reaction'
        )
