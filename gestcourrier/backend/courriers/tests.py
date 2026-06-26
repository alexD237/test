import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from courriers.models import Courrier
from utilisateurs.models import Utilisateur

PDF_VALIDE = b"%PDF-1.4\n%minimal valid pdf\n"


def pdf_upload(nom="scan.pdf", contenu=PDF_VALIDE):
    return SimpleUploadedFile(nom, contenu, content_type="application/pdf")


class CourrierTests(APITestCase):
    def setUp(self):
        media = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.agent = Utilisateur.objects.create_user(
            username="5487-T", password="a", nom_complet="Agent BC", role=Utilisateur.Role.AGENT
        )
        self.admin = Utilisateur.objects.create_user(
            username="0001-A", password="a", nom_complet="Admin", role=Utilisateur.Role.ADMIN
        )

    def auth(self, user):
        token = self.client.post(
            "/api/auth/login/", {"username": user.username, "password": "a"}
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def depot_entrant(self, numero="004901-26"):
        return self.client.post(
            "/api/courriers/",
            {
                "numero": numero,
                "type_courrier": "ENTRANT",
                "date_courrier": "2026-06-25",
                "correspondant": "Direction Générale",
                "service_interne": "DRH",
                "objet": "Demande de congé",
                "fichier_pdf": pdf_upload(),
            },
            format="multipart",
        )

    def test_acces_anonyme_refuse(self):
        response = self.client.get("/api/courriers/")
        self.assertEqual(response.status_code, 401)

    def test_depot_entrant_ok(self):
        self.auth(self.agent)
        response = self.depot_entrant()
        self.assertEqual(response.status_code, 201)
        courrier = Courrier.objects.get(numero="004901-26")
        self.assertEqual(courrier.depose_par, self.agent)
        self.assertIn("entrants/2026/004901-26.pdf", courrier.fichier_pdf.name)

    def test_numero_format_invalide_refuse(self):
        self.auth(self.agent)
        response = self.depot_entrant(numero="ABC-26")
        self.assertEqual(response.status_code, 400)
        self.assertIn("numero", response.data)

    def test_sortant_sans_signataire_refuse(self):
        self.auth(self.agent)
        response = self.client.post(
            "/api/courriers/",
            {
                "numero": "002201-26",
                "type_courrier": "SORTANT",
                "date_courrier": "2026-06-25",
                "correspondant": "Ministère",
                "objet": "Réponse officielle",
                "fichier_pdf": pdf_upload(),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("signataire", response.data)

    def test_fichier_non_pdf_refuse(self):
        self.auth(self.agent)
        response = self.client.post(
            "/api/courriers/",
            {
                "numero": "004902-26",
                "type_courrier": "ENTRANT",
                "date_courrier": "2026-06-25",
                "correspondant": "DG",
                "service_interne": "DRH",
                "objet": "Test",
                "fichier_pdf": pdf_upload(nom="faux.pdf", contenu=b"je ne suis pas un pdf"),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("fichier_pdf", response.data)

    def test_telechargement_pdf(self):
        self.auth(self.agent)
        self.depot_entrant()
        courrier = Courrier.objects.get(numero="004901-26")
        response = self.client.get(f"/api/courriers/{courrier.id}/pdf/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_agent_ne_peut_pas_supprimer(self):
        self.auth(self.agent)
        self.depot_entrant()
        courrier = Courrier.objects.get(numero="004901-26")
        response = self.client.delete(f"/api/courriers/{courrier.id}/")
        self.assertEqual(response.status_code, 403)

    def test_admin_suppression_logique(self):
        self.auth(self.agent)
        self.depot_entrant()
        courrier = Courrier.objects.get(numero="004901-26")
        self.auth(self.admin)
        response = self.client.delete(f"/api/courriers/{courrier.id}/")
        self.assertEqual(response.status_code, 204)
        courrier.refresh_from_db()
        self.assertTrue(courrier.supprime)
        self.assertEqual(self.client.get("/api/courriers/").data["count"], 0)
