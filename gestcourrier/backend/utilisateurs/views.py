from rest_framework_simplejwt.views import TokenObtainPairView

from utilisateurs.serializers import GestCourrierTokenSerializer


class LoginView(TokenObtainPairView):
    serializer_class = GestCourrierTokenSerializer
