import uuid

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
