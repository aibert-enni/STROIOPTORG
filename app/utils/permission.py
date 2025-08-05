from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Менеджер').exists()

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Админ').exists()