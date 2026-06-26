from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class GestCourrierTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["nom_complet"] = user.nom_complet
        token["role"] = user.role
        return token
