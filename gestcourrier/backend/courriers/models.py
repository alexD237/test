import uuid

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify

NUMERO_VALIDATOR = RegexValidator(
    regex=r"^\d{6}-\d{2}$",
    message="Le numéro doit être au format XXXXXX-AA (ex : 004901-26).",
)


def chemin_pdf(courrier, nom_fichier_origine):
    """media/courriers/{entrants|sortants}/{annee}/{numero}.pdf

    Le nom de fichier est dérivé du numéro (slugifié) — aucun nom fourni
    par l'utilisateur n'est utilisé tel quel (CDC 5.2).
    """
    dossier = "entrants" if courrier.type_courrier == Courrier.Type.ENTRANT else "sortants"
    annee = courrier.date_courrier.year
    return f"courriers/{dossier}/{annee}/{slugify(courrier.numero)}.pdf"


class Courrier(models.Model):
    class Type(models.TextChoices):
        ENTRANT = "ENTRANT", "Entrant"
        SORTANT = "SORTANT", "Sortant"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=20, unique=True, validators=[NUMERO_VALIDATOR])
    type_courrier = models.CharField(max_length=10, choices=Type.choices)
    date_courrier = models.DateField()
    correspondant = models.CharField(max_length=200)
    service_interne = models.CharField(max_length=100, blank=True)
    signataire = models.CharField(max_length=100, blank=True)
    objet = models.TextField(max_length=300)
    annotations_directeur = models.TextField(blank=True)
    observation = models.TextField(blank=True)
    fichier_pdf = models.FileField(upload_to=chemin_pdf, max_length=500)
    date_depot = models.DateTimeField(auto_now_add=True)
    depose_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="courriers"
    )
    supprime = models.BooleanField(default=False)
    # Alimenté par un trigger PostgreSQL (config 'french') — voir migration.
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ["-date_courrier", "-date_depot"]
        indexes = [GinIndex(fields=["search_vector"])]

    def __str__(self):
        return f"{self.numero} ({self.type_courrier})"
