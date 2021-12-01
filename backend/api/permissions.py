from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        method = request.method
        if method == 'GET' and (user.is_anonymous or user.is_authenticated):
            return True
        elif method in ['POST', 'DELETE', 'PUT'] and user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method
        if method == 'GET' and (user.is_anonymous or user.is_authenticated):
            return True
        elif obj.author == user and method in ['DELETE', 'PUT']:
            return True
        return False
