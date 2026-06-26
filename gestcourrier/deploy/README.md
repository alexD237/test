# Déploiement ArchivRH (intranet PAD)

Déploiement on-premise sur le réseau interne du Port Autonome de Douala.
Aucune connexion Internet n'est requise au runtime : toutes les dépendances
(polices, PDF.js, bibliothèques Python) sont embarquées.

## Architecture

```
Navigateur (intranet DRH)
        │ HTTPS
        ▼
     Nginx ──── /static/  → fichiers Django (collectstatic)
        │  ──── /          → build React (frontend/dist)
        │  ──── /api/      → proxy
        ▼
   Gunicorn (127.0.0.1:8000) → Django
        ▼
   PostgreSQL 15   +   MEDIA_ROOT (PDF, jamais exposé par Nginx)
```

## Prérequis serveur

- Ubuntu 22.04, Python 3.11, Node 20+, PostgreSQL 15, Nginx
- Dépendances système WeasyPrint : `libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0`

## Backend

```bash
cd /opt/gestcourrier/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # puis renseigner SECRET_KEY, DB_*, ALLOWED_HOSTS (DEBUG=False)
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # premier compte ADMIN
```

Service Gunicorn :

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/gestcourrier.service
sudo mkdir -p /var/log/gestcourrier && sudo chown gestcourrier /var/log/gestcourrier
sudo systemctl enable --now gestcourrier
```

## Frontend

```bash
cd /opt/gestcourrier/frontend
npm ci
npm run build        # génère frontend/dist servi par Nginx
```

## Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/gestcourrier
sudo ln -s /etc/nginx/sites-available/gestcourrier /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Adapter `server_name`, les chemins des certificats TLS et les chemins
`/opt/gestcourrier/...` à l'installation réelle.

## Sécurité (rappels CDC)

- Les PDF ne sont accessibles que via `/api/courriers/{id}/pdf/` (JWT) — Nginx
  n'expose jamais `MEDIA_ROOT`.
- `DEBUG=False` active la redirection HTTPS, HSTS et les cookies sécurisés.
- Verrouillage de compte après 5 échecs (15 min), déconnexion auto après 30 min.
- Journal d'audit immuable, export CSV réservé à l'administrateur.
