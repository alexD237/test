from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from rest_framework.response import Response
from weasyprint import HTML

from reporting.services import agregats_mensuels, parse_mois

NOMS_MOIS = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


@api_view(["GET"])
def rapport_mensuel(request):
    annee, mois = parse_mois(request.query_params.get("mois"))
    return Response(agregats_mensuels(annee, mois))


@api_view(["GET"])
def export_pdf(request):
    annee, mois = parse_mois(request.query_params.get("mois"))
    contexte = agregats_mensuels(annee, mois)
    contexte["nom_mois"] = NOMS_MOIS[mois]
    html = render_to_string("reporting/rapport.html", contexte)
    pdf = HTML(string=html).write_pdf()
    reponse = HttpResponse(pdf, content_type="application/pdf")
    reponse["Content-Disposition"] = f'attachment; filename="rapport-{annee}-{mois:02d}.pdf"'
    return reponse
