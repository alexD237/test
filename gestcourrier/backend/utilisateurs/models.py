import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        AGENT = "AGENT", "Agent bureau courrier"
        ADMIN = "ADMIN", "Administrateur technique"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_complet = models.CharField(max_length=200)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.AGENT)

    def __str__(self):
        return f"{self.username} ({self.role})"


class AuditLog(models.Model):
    class Action(models.TextChoices):
        DEPOT = "DEPOT", "Dépôt"
        CONSULTATION = "CONSULTATION", "Consultation"
        TELECHARGEMENT = "TELECHARGEMENT", "Téléchargement"
        MODIFICATION = "MODIFICATION", "Modification"
        SUPPRESSION = "SUPPRESSION", "Suppression"
        CONNEXION = "CONNEXION", "Connexion"
        ADMIN = "ADMIN", "Administration"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="actions"
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    courrier = models.ForeignKey(
        "courriers.Courrier", on_delete=models.SET_NULL, null=True, blank=True
    )
    detail = models.TextField(blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    horodatage = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-horodatage"]

    def __str__(self):
        return f"{self.horodatage:%Y-%m-%d %H:%M} {self.utilisateur} {self.action}"
