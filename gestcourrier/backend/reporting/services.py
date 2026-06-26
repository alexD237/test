from datetime import date

from django.db.models import Count

from courriers.models import Courrier


def parse_mois(valeur):
    if valeur:
        annee, mois = valeur.split("-")
        return int(annee), int(mois)
    aujourdhui = date.today()
    return aujourdhui.year, aujourdhui.month


def agregats_mensuels(annee, mois):
    qs = Courrier.objects.filter(supprime=False, date_courrier__year=annee, date_courrier__month=mois)
    total = qs.count()
    avec_pdf = qs.exclude(fichier_pdf="").count()

    par_service = list(
        qs.filter(type_courrier=Courrier.Type.ENTRANT)
        .exclude(service_interne="")
        .values("service_interne")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    par_signataire = list(
        qs.filter(type_courrier=Courrier.Type.SORTANT)
        .exclude(signataire="")
        .values("signataire")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    return {
        "annee": annee,
        "mois": mois,
        "total": total,
        "total_entrants": qs.filter(type_courrier=Courrier.Type.ENTRANT).count(),
        "total_sortants": qs.filter(type_courrier=Courrier.Type.SORTANT).count(),
        "taux_numerise": round(avec_pdf / total * 100, 1) if total else 0,
        "par_service": par_service,
        "par_signataire": par_signataire,
    }
