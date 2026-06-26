import csv
import os
import shutil

from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from utilisateurs.audit import enregistrer
from utilisateurs.models import AuditLog, Utilisateur
from utilisateurs.permissions import IsAdmin
from utilisateurs.serializers import AuditLogSerializer, UtilisateurSerializer


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.order_by("username")
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def perform_create(self, serializer):
        utilisateur = serializer.save()
        enregistrer(self.request, AuditLog.Action.ADMIN, detail=f"Création du compte {utilisateur.username}")

    def perform_update(self, serializer):
        utilisateur = serializer.save()
        enregistrer(self.request, AuditLog.Action.ADMIN, detail=f"Modification du compte {utilisateur.username}")


def filtrer_audit(params):
    qs = AuditLog.objects.select_related("utilisateur", "courrier")
    if params.get("action"):
        qs = qs.filter(action=params["action"])
    if params.get("utilisateur"):
        qs = qs.filter(utilisateur__username=params["utilisateur"])
    return qs


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return filtrer_audit(self.request.query_params)


@api_view(["GET"])
@permission_classes([IsAdmin])
def export_audit_csv(request):
    reponse = HttpResponse(content_type="text/csv")
    reponse["Content-Disposition"] = 'attachment; filename="journal-audit.csv"'
    writer = csv.writer(reponse)
    writer.writerow(["Horodatage (UTC)", "Matricule", "Nom", "Action", "Courrier", "Détail", "Adresse IP"])
    for log in filtrer_audit(request.query_params):
        writer.writerow([
            log.horodatage.strftime("%Y-%m-%d %H:%M:%S"),
            log.utilisateur.username,
            log.utilisateur.nom_complet,
            log.action,
            log.courrier.numero if log.courrier else "",
            log.detail,
            log.adresse_ip or "",
        ])
    return reponse


@api_view(["GET"])
@permission_classes([IsAdmin])
def stats_systeme(request):
    racine = os.path.join(settings.MEDIA_ROOT, "courriers")
    nombre, total = 0, 0
    for dossier, _, fichiers in os.walk(racine):
        for nom in fichiers:
            nombre += 1
            total += os.path.getsize(os.path.join(dossier, nom))
    disque = shutil.disk_usage(settings.MEDIA_ROOT)
    return Response({
        "nombre_fichiers": nombre,
        "espace_utilise_octets": total,
        "taille_moyenne_octets": round(total / nombre) if nombre else 0,
        "disque_total_octets": disque.total,
        "disque_libre_octets": disque.free,
    })
