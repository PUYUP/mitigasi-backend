from rest_framework import permissions


class IsActivityCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.activity.user.id == request.user.id
