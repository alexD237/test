from utilisateurs.models import AuditLog


def adresse_ip(request):
    transfere = request.META.get("HTTP_X_FORWARDED_FOR")
    if transfere:
        return transfere.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def enregistrer(request, action, courrier=None, detail=""):
    AuditLog.objects.create(
        utilisateur=request.user,
        action=action,
        courrier=courrier,
        detail=detail,
        adresse_ip=adresse_ip(request),
    )
