from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import permissions

Activity = apps.get_registered_model('generic', 'Activity')


class IsHazardAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        ct = ContentType.objects.get_for_model(obj.__class__)

        try:
            activity_obj = Activity.objects.get(
                content_type_id=ct.id,
                object_id=obj.id
            )
        except ObjectDoesNotExist:
            # Just return no permission
            return False

        return activity_obj.user.id == request.user.id
