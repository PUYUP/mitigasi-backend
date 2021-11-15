from django.apps import apps

Activity = apps.get_registered_model('generic', 'Activity')


def _create_activity(instance):
    # `request` inject to model from middleware
    request = getattr(Activity, 'request')

    # note! `user` must logged in if not raise `ValueError`
    Activity.objects.create(
        user=request.user,
        content_object=instance
    )


def create_comment(sender, instance, created, **kwargs):
    pass


def create_confirmation(sender, instance, created, **kwargs):
    pass


def create_reaction(sender, instance, created, **kwargs):
    pass
