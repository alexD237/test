import tempfile
import time

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from utilisateurs.models import Utilisateur

PDF_VALIDE = b"%PDF-1.4\n%minimal valid pdf\n"


def pdf_upload(nom="scan.pdf"):
    return SimpleUploadedFile(nom, PDF_VALIDE, content_type="application/pdf")


class ReportingTests(APITestCase):
    def setUp(self):
        media = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)
        self.agent = Utilisateur.objects.create_user(
            username="5487-T", password="a", nom_complet="Agent BC", role=Utilisateur.Role.AGENT
        )
        token = self.client.post(
            "/api/auth/login/", {"username": "5487-T", "password": "a"}
        ).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def depot(self, numero, type_courrier="ENTRANT", date="2026-06-10", **extra):
        data = {
            "numero": numero,
            "type_courrier": type_courrier,
            "date_courrier": date,
            "correspondant": "DG",
            "objet": "objet",
            "fichier_pdf": pdf_upload(),
        }
        if type_courrier == "ENTRANT":
            data["service_interne"] = extra.pop("service_interne", "DRH")
        else:
            data["signataire"] = extra.pop("signataire", "DG")
        data.update(extra)
        return self.client.post("/api/courriers/", data, format="multipart")

    def test_agregats_mensuels(self):
        self.depot("004901-26", "ENTRANT", service_interne="DRH")
        self.depot("004902-26", "ENTRANT", service_interne="DRH")
        self.depot("002201-26", "SORTANT", signataire="DG")
        self.depot("004903-26", "ENTRANT", date="2026-01-05", service_interne="CMS")

        response = self.client.get("/api/reporting/mensuel/", {"mois": "2026-06"})
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["total_entrants"], 2)
        self.assertEqual(data["total_sortants"], 1)
        self.assertEqual(data["taux_numerise"], 100.0)
        self.assertEqual(data["par_service"], [{"service_interne": "DRH", "total": 2}])
        self.assertEqual(data["par_signataire"], [{"signataire": "DG", "total": 1}])
        # Tous déposés le 10 du mois -> semaine 2.
        self.assertEqual(data["par_semaine"][1], {"semaine": 2, "entrants": 2, "sortants": 1})
        self.assertEqual(len(data["par_semaine"]), 5)

    def test_mois_sans_courrier(self):
        response = self.client.get("/api/reporting/mensuel/", {"mois": "2020-01"})
        self.assertEqual(response.data["total"], 0)
        self.assertEqual(response.data["taux_numerise"], 0)

    def test_export_pdf(self):
        self.depot("004901-26", "ENTRANT", service_interne="DRH")
        debut = time.monotonic()
        response = self.client.get("/api/reporting/export-pdf/", {"mois": "2026-06"})
        duree = time.monotonic() - debut
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertLess(duree, 5)
