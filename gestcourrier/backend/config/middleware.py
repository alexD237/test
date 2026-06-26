# CSP et en-têtes de sécurité complémentaires (CDC 5.3).
# L'app React et l'API sont servies sous la même origine (Nginx), donc une CSP
# stricte suffit : pas de ressources externes en production.
CSP = (
    "default-src 'self'; "
    "img-src 'self' data: blob:; "
    "style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", CSP)
        response.setdefault("Referrer-Policy", "same-origin")
        response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response
