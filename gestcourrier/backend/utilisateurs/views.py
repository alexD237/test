from rest_framework_simplejwt.views import TokenObtainPairView

from utilisateurs.audit import adresse_ip
from utilisateurs.models import AuditLog, Utilisateur
from utilisateurs.serializers import GestCourrierTokenSerializer


class LoginView(TokenObtainPairView):
    serializer_class = GestCourrierTokenSerializer

    def post(self, request, *args, **kwargs):
        # request.user est anonyme lors du login : on retrouve l'auteur via le matricule.
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            utilisateur = Utilisateur.objects.get(username=request.data["username"])
            AuditLog.objects.create(
                utilisateur=utilisateur,
                action=AuditLog.Action.CONNEXION,
                adresse_ip=adresse_ip(request),
            )
        return response
