from rest_framework.permissions import BasePermission

from utilisateurs.models import Utilisateur


class CourrierPermission(BasePermission):
    """Agents et admins gèrent les courriers ; seul l'admin peut supprimer."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "DELETE":
            return request.user.role == Utilisateur.Role.ADMIN
        return True
