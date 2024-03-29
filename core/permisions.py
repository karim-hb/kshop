from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from rest_framework import permissions


class IsAminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
