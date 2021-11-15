from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

Activity = apps.get_registered_model('contribution', 'Activity')


class ActivityCreateMixin(object):
    """Create :activity then insert to internal value data"""
    @transaction.atomic
    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        user = self.context.get('request').user
        model_name = self.Meta.model._meta.model_name
        model_ct = ContentType.objects.get(model=model_name)

        activity_obj = Activity.objects.create(
            user=user,
            content_type=model_ct
        )

        data.update({'activity': activity_obj})
        return data
