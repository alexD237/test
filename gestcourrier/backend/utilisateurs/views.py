from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from utilisateurs.audit import adresse_ip
from utilisateurs.models import AuditLog, Utilisateur
from utilisateurs.serializers import GestCourrierTokenSerializer


class LoginView(TokenObtainPairView):
    serializer_class = GestCourrierTokenSerializer

    def post(self, request, *args, **kwargs):
        # request.user est anonyme lors du login : on retrouve l'auteur via le matricule.
        utilisateur = Utilisateur.objects.filter(username=request.data.get("username")).first()

        if utilisateur and utilisateur.verrouille_jusqu and utilisateur.verrouille_jusqu > timezone.now():
            return Response(
                {"detail": "Compte verrouillé après plusieurs échecs. Réessayez plus tard."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            if utilisateur:
                utilisateur.echecs_connexion += 1
                if utilisateur.echecs_connexion >= settings.MAX_ECHECS_CONNEXION:
                    utilisateur.verrouille_jusqu = timezone.now() + settings.DUREE_VERROUILLAGE
                utilisateur.save(update_fields=["echecs_connexion", "verrouille_jusqu"])
            raise

        if utilisateur:
            utilisateur.echecs_connexion = 0
            utilisateur.verrouille_jusqu = None
            utilisateur.save(update_fields=["echecs_connexion", "verrouille_jusqu"])
        AuditLog.objects.create(
            utilisateur=utilisateur,
            action=AuditLog.Action.CONNEXION,
            adresse_ip=adresse_ip(request),
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
