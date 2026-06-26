from django.urls import path

from reporting.views import export_pdf, rapport_mensuel

urlpatterns = [
    path("reporting/mensuel/", rapport_mensuel),
    path("reporting/export-pdf/", export_pdf),
]
