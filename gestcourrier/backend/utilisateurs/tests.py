import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase

from courriers.models import Courrier
from utilisateurs.models import AuditLog, Utilisateur

PDF_VALIDE = b"%PDF-1.4\n%minimal valid pdf\n"


def pdf_upload():
    return SimpleUploadedFile("scan.pdf", PDF_VALIDE, content_type="application/pdf")


class AuthTests(APITestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            username="5487-T", password="a", nom_complet="Jean Test", role=Utilisateur.Role.AGENT
        )

    def test_login_avec_matricule_et_mot_de_passe_arbitraire(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "5487-T", "password": "a"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_mauvais_mot_de_passe_refuse(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "5487-T", "password": "mauvais"}
        )
        self.assertEqual(response.status_code, 401)

    def test_refresh_renvoie_un_nouveau_access_token(self):
        login = self.client.post(
            "/api/auth/login/", {"username": "5487-T", "password": "a"}
        )
        response = self.client.post(
            "/api/auth/refresh/", {"refresh": login.data["refresh"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


class EntetesSecuriteTests(APITestCase):
    def test_entetes_presents(self):
        response = self.client.get("/api/courriers/")
        self.assertIn("Content-Security-Policy", response)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Referrer-Policy"], "same-origin")


class VerrouillageTests(APITestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            username="5487-T", password="bonmotdepasse", nom_complet="Jean", role=Utilisateur.Role.AGENT
        )

    def echec(self):
        return self.client.post("/api/auth/login/", {"username": "5487-T", "password": "faux"})

    def test_verrouillage_apres_cinq_echecs(self):
        for _ in range(4):
            self.assertEqual(self.echec().status_code, 401)
        self.assertEqual(self.echec().status_code, 401)
        # 5e échec atteint -> compte verrouillé, même le bon mot de passe est refusé.
        bloque = self.client.post("/api/auth/login/", {"username": "5487-T", "password": "bonmotdepasse"})
        self.assertEqual(bloque.status_code, 429)

    def test_succes_remet_le_compteur_a_zero(self):
        self.echec()
        self.echec()
        self.client.post("/api/auth/login/", {"username": "5487-T", "password": "bonmotdepasse"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.echecs_connexion, 0)
        self.assertIsNone(self.user.verrouille_jusqu)


class BaseAdmin(APITestCase):
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


class AdminUtilisateursTests(BaseAdmin):
    def test_agent_refuse(self):
        self.auth(self.agent)
        self.assertEqual(self.client.get("/api/admin/utilisateurs/").status_code, 403)

    def test_admin_cree_compte_matricule(self):
        self.auth(self.admin)
        response = self.client.post(
            "/api/admin/utilisateurs/",
            {"username": "9920-K", "nom_complet": "Nouveau", "role": "AGENT", "password": "nimportequoi"},
        )
        self.assertEqual(response.status_code, 201)
        nouveau = Utilisateur.objects.get(username="9920-K")
        self.assertTrue(nouveau.check_password("nimportequoi"))
        self.assertTrue(AuditLog.objects.filter(action="ADMIN").exists())

    def test_admin_desactive_compte(self):
        self.auth(self.admin)
        response = self.client.patch(
            f"/api/admin/utilisateurs/{self.agent.id}/", {"is_active": False}
        )
        self.assertEqual(response.status_code, 200)
        self.agent.refresh_from_db()
        self.assertFalse(self.agent.is_active)

    def test_admin_reinitialise_mot_de_passe(self):
        self.auth(self.admin)
        self.client.patch(f"/api/admin/utilisateurs/{self.agent.id}/", {"password": "reset123"})
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.check_password("reset123"))


class AuditTests(BaseAdmin):
    def depot(self, numero="004901-26"):
        return self.client.post(
            "/api/courriers/",
            {
                "numero": numero,
                "type_courrier": "ENTRANT",
                "date_courrier": "2026-06-25",
                "correspondant": "DG",
                "service_interne": "DRH",
                "objet": "Test",
                "fichier_pdf": pdf_upload(),
            },
            format="multipart",
        )

    def test_connexion_journalisee(self):
        self.auth(self.agent)
        self.assertTrue(
            AuditLog.objects.filter(utilisateur=self.agent, action="CONNEXION").exists()
        )

    def test_depot_et_telechargement_journalises(self):
        self.auth(self.agent)
        self.depot()
        courrier = Courrier.objects.get(numero="004901-26")
        self.client.get(f"/api/courriers/{courrier.id}/pdf/")
        self.assertTrue(AuditLog.objects.filter(action="DEPOT", courrier=courrier).exists())
        self.assertTrue(AuditLog.objects.filter(action="TELECHARGEMENT", courrier=courrier).exists())

    def test_journal_filtre_par_action(self):
        self.auth(self.agent)
        self.depot()
        self.auth(self.admin)
        response = self.client.get("/api/admin/audit/", {"action": "DEPOT"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(l["action"] == "DEPOT" for l in response.data["results"]))
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_export_csv(self):
        self.auth(self.agent)
        self.depot()
        self.auth(self.admin)
        response = self.client.get("/api/admin/audit/export-csv/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("DEPOT", response.content.decode())

    def test_audit_immuable_pas_de_delete(self):
        self.auth(self.admin)
        self.client.post(
            "/api/admin/utilisateurs/",
            {"username": "1212-Z", "nom_complet": "X", "role": "AGENT", "password": "x"},
        )
        log = AuditLog.objects.first()
        response = self.client.delete(f"/api/admin/audit/{log.id}/")
        self.assertEqual(response.status_code, 405)


class StatsTests(BaseAdmin):
    def test_stats_systeme(self):
        self.auth(self.agent)
        self.client.post(
            "/api/courriers/",
            {
                "numero": "004901-26",
                "type_courrier": "ENTRANT",
                "date_courrier": "2026-06-25",
                "correspondant": "DG",
                "service_interne": "DRH",
                "objet": "Test",
                "fichier_pdf": pdf_upload(),
            },
            format="multipart",
        )
        self.auth(self.admin)
        response = self.client.get("/api/admin/stats-systeme/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["nombre_fichiers"], 1)
        self.assertGreater(response.data["espace_utilise_octets"], 0)
