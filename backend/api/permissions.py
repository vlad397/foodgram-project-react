from rest_framework.permissions import BasePermission


class CustomPermission(BasePermission):
    methods = ['POST', 'DELETE', 'PUT', 'PATCH']

    def has_permission(self, request, view):
        user = request.user
        method = request.method
        if method == 'GET':
            return True
        elif method in self.methods and user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        method = request.method
        if method == 'GET':
            return True
        elif obj.author == user and method in ['DELETE', 'PUT', 'PATCH']:
            return True
        return False
