from django.contrib.postgres.search import SearchQuery, SearchRank
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from courriers.models import Courrier
from courriers.permissions import CourrierPermission
from courriers.serializers import CourrierSerializer
from utilisateurs.audit import enregistrer
from utilisateurs.models import AuditLog

ORDERINGS = {
    "date": "date_courrier",
    "-date": "-date_courrier",
    "numero": "numero",
    "-numero": "-numero",
}


class CourrierViewSet(viewsets.ModelViewSet):
    serializer_class = CourrierSerializer
    permission_classes = [CourrierPermission]

    def get_queryset(self):
        qs = Courrier.objects.filter(supprime=False)
        params = self.request.query_params

        recherche = params.get("q")
        if recherche:
            query = SearchQuery(recherche, config="french")
            qs = qs.filter(search_vector=query).annotate(
                rang=SearchRank("search_vector", query)
            )

        if params.get("type"):
            qs = qs.filter(type_courrier=params["type"])
        if params.get("numero"):
            qs = qs.filter(numero__icontains=params["numero"])
        if params.get("service"):
            qs = qs.filter(service_interne=params["service"])
        if params.get("signataire"):
            qs = qs.filter(signataire=params["signataire"])
        if params.get("date_debut"):
            qs = qs.filter(date_courrier__gte=params["date_debut"])
        if params.get("date_fin"):
            qs = qs.filter(date_courrier__lte=params["date_fin"])
        avec_pdf = params.get("avec_pdf")
        if avec_pdf == "true":
            qs = qs.exclude(fichier_pdf="")
        elif avec_pdf == "false":
            qs = qs.filter(fichier_pdf="")

        tri = params.get("tri")
        if tri in ORDERINGS:
            qs = qs.order_by(ORDERINGS[tri])
        elif recherche:
            qs = qs.order_by("-rang")
        return qs

    def perform_create(self, serializer):
        courrier = serializer.save(depose_par=self.request.user)
        enregistrer(self.request, AuditLog.Action.DEPOT, courrier, courrier.numero)

    def perform_update(self, serializer):
        courrier = serializer.save()
        enregistrer(self.request, AuditLog.Action.MODIFICATION, courrier, courrier.numero)

    def perform_destroy(self, instance):
        # Suppression logique (CDC 3.3) — le fichier et la ligne sont conservés.
        instance.supprime = True
        instance.save(update_fields=["supprime"])
        enregistrer(self.request, AuditLog.Action.SUPPRESSION, instance, instance.numero)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        enregistrer(request, AuditLog.Action.CONSULTATION, self.get_object(), self.get_object().numero)
        return response

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        courrier = self.get_object()
        enregistrer(request, AuditLog.Action.TELECHARGEMENT, courrier, courrier.numero)
        return FileResponse(
            courrier.fichier_pdf.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{courrier.numero}.pdf",
        )
