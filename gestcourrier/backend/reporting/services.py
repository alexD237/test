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

    # Répartition entrants/sortants par semaine du mois (CDC 2.4).
    par_semaine = [{"semaine": i + 1, "entrants": 0, "sortants": 0} for i in range(5)]
    for jour, type_courrier in qs.values_list("date_courrier", "type_courrier"):
        index = min((jour.day - 1) // 7, 4)
        cle = "entrants" if type_courrier == Courrier.Type.ENTRANT else "sortants"
        par_semaine[index][cle] += 1

    return {
        "annee": annee,
        "mois": mois,
        "total": total,
        "total_entrants": qs.filter(type_courrier=Courrier.Type.ENTRANT).count(),
        "total_sortants": qs.filter(type_courrier=Courrier.Type.SORTANT).count(),
        "taux_numerise": round(avec_pdf / total * 100, 1) if total else 0,
        "par_service": par_service,
        "par_signataire": par_signataire,
        "par_semaine": par_semaine,
    }
