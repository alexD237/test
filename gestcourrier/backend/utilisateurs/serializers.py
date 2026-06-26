from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from utilisateurs.models import AuditLog, Utilisateur


class GestCourrierTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["nom_complet"] = user.nom_complet
        token["role"] = user.role
        return token


class UtilisateurSerializer(serializers.ModelSerializer):
    # Aucune contrainte de complexité sur le mot de passe (choix DRH).
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Utilisateur
        fields = ["id", "username", "nom_complet", "role", "is_active", "date_joined", "last_login", "password"]
        read_only_fields = ["id", "date_joined", "last_login"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Mot de passe obligatoire à la création."})
        utilisateur = Utilisateur(**validated_data)
        utilisateur.set_password(password)
        utilisateur.save()
        return utilisateur

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for champ, valeur in validated_data.items():
            setattr(instance, champ, valeur)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AuditLogSerializer(serializers.ModelSerializer):
    utilisateur = serializers.CharField(source="utilisateur.username", read_only=True)
    nom_complet = serializers.CharField(source="utilisateur.nom_complet", read_only=True)
    numero = serializers.CharField(source="courrier.numero", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = ["id", "utilisateur", "nom_complet", "action", "numero", "detail", "adresse_ip", "horodatage"]
