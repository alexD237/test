from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from courriers.models import Courrier
from courriers.permissions import CourrierPermission
from courriers.serializers import CourrierSerializer


class CourrierViewSet(viewsets.ModelViewSet):
    serializer_class = CourrierSerializer
    permission_classes = [CourrierPermission]

    def get_queryset(self):
        return Courrier.objects.filter(supprime=False)

    def perform_create(self, serializer):
        serializer.save(depose_par=self.request.user)

    def perform_destroy(self, instance):
        # Suppression logique (CDC 3.3) — le fichier et la ligne sont conservés.
        instance.supprime = True
        instance.save(update_fields=["supprime"])

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        courrier = self.get_object()
        return FileResponse(
            courrier.fichier_pdf.open("rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{courrier.numero}.pdf",
        )
