from rest_framework.permissions import BasePermission

from utilisateurs.models import Utilisateur


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Utilisateur.Role.ADMIN
        )
