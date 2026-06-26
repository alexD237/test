import magic
from django.conf import settings
from rest_framework import serializers

from courriers.models import Courrier


class CourrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courrier
        fields = [
            "id",
            "numero",
            "type_courrier",
            "date_courrier",
            "correspondant",
            "service_interne",
            "signataire",
            "objet",
            "annotations_directeur",
            "observation",
            "fichier_pdf",
            "date_depot",
            "depose_par",
        ]
        read_only_fields = ["id", "date_depot", "depose_par"]

    def validate_fichier_pdf(self, fichier):
        if fichier.size > settings.MAX_PDF_SIZE:
            raise serializers.ValidationError("Le fichier dépasse la taille maximale de 20 Mo.")
        en_tete = fichier.read(2048)
        fichier.seek(0)
        if magic.from_buffer(en_tete, mime=True) != "application/pdf":
            raise serializers.ValidationError("Le fichier doit être un PDF valide.")
        return fichier

    def validate(self, data):
        # Sur un PATCH partiel, on retombe sur le type déjà enregistré.
        type_courrier = data.get(
            "type_courrier", getattr(self.instance, "type_courrier", None)
        )
        if type_courrier == Courrier.Type.ENTRANT:
            service = data.get("service_interne", getattr(self.instance, "service_interne", ""))
            if not service:
                raise serializers.ValidationError(
                    {"service_interne": "Obligatoire pour un courrier entrant."}
                )
        elif type_courrier == Courrier.Type.SORTANT:
            signataire = data.get("signataire", getattr(self.instance, "signataire", ""))
            if not signataire:
                raise serializers.ValidationError(
                    {"signataire": "Obligatoire pour un courrier sortant."}
                )
        return data
