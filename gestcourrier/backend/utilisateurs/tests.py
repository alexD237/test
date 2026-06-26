from rest_framework.test import APITestCase

from utilisateurs.models import Utilisateur


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
