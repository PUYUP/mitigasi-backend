from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from rest_framework import permissions

Activity = apps.get_registered_model('generic', 'Activity')


class IsActivityAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user.id == request.user.id


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        ct = ContentType.objects.get_for_model(obj.__class__)
        activity_obj = Activity.objects.get(
            content_type_id=ct.id,
            object_id=obj.id
        )

        return activity_obj.user.id == request.user.id
