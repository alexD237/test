from django.urls import path
from rest_framework.routers import DefaultRouter

from utilisateurs.admin_views import (
    AuditLogViewSet,
    UtilisateurViewSet,
    export_audit_csv,
    stats_systeme,
)

router = DefaultRouter()
router.register("utilisateurs", UtilisateurViewSet, basename="admin-utilisateur")
router.register("audit", AuditLogViewSet, basename="admin-audit")

urlpatterns = [
    path("audit/export-csv/", export_audit_csv),
    path("stats-systeme/", stats_systeme),
    *router.urls,
]
